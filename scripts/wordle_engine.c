#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { WORDLEN = 5, BASE = 3, TOTAL_PATTERNS = 243, GREEN = 0, YELLOW = 1, GREY = 2 };
uint8_t* pattern_matrix = NULL;

/**
 * @brief Computes the Wordle pattern between a guess and target word.
 *
 * @param guess  The guessed word string (must be length WORDLEN).
 * @param target The actual target word string (must be length WORDLEN).
 * @return uint8_t A Base-3 integer representing the pattern (0 to 242).
 *
 * @details
 * **Performance Optimization: Horner's Method**
 * To convert the Base-3 pattern array {A_n-1, A_n-2, ..., A_0} into a Base-10 integer,
 * the naive approach calculates A[i] * pow(3, i). However, using <math.h> pow() 
 * invokes floating-point math, which incurs massive CPU overhead in a tight loop.
 * * Instead, we use Horner's Method. By initializing `sum = 0` and iterating 
 * left-to-right, the Base-10 equivalent is calculated natively via:
 * * sum = (sum * base) + A[i]
 * * This reduces the operation to a single hardware multiplication and addition 
 * per digit, executing in a single clock cycle without floating-point overhead.
 */
uint8_t compute_pattern(const char guess[WORDLEN + 1], const char target[WORDLEN + 1])
{
    uint8_t pattern[WORDLEN];
    int target_count[26] = {0};

    for (int i = 0; i < WORDLEN; i++) {
      if (guess[i] == target[i]) {
        pattern[i] = GREEN;
      }
      else {
        // 'a' - 'a' = 0; 'b' - 'a' = 1 and so on....
        target_count[target[i] - 'a']++;
        pattern[i] = GREY;
      }
    }

    for (int i = 0; i < WORDLEN; i++) {
      if (pattern[i] != GREEN) {
        int char_index = guess[i] - 'a';
        if (target_count[char_index]) {
          pattern[i] = YELLOW;
          target_count[char_index]--;
        }
      }
    }

    uint8_t pattern_value = 0;
    for (int i = 0; i < WORDLEN; i++) {
        pattern_value = (pattern_value * BASE) + pattern[i];
    }

    return pattern_value;
}

/**
 * @brief Generates a precomputed pattern matrix containing the integer values calculated in compute_pattern.
 *
 * @param words        Array of strings containing all the words.
 * @param total_words  Number of words in the array.
 *
 * @details
 * Essentially, this generates a LUT for patterns. After the initial pass of all the words against each other
 * to calculate entropy, we already know all the patterns for each pair of words (the pattern between 
 * APPLE and SLATE will always be the same), so from the 2nd pass, we can just see the pair of words and
 * go to the memory address of the pair of words to get the corresponding pattern. 
 * This makes it an O(1) operation, which will be extremely fast.
 *
 * The matrix is a flat 1D array laid out in row-major order, representing
 * a 2D array where rows are guesses and columns are targets:
 *
 * index of pattern_matrix[i][j] = i * total_words + j
 *
 * This follows the standard row-major address formula:
 *
 * Address of A[I][J] = B + W * ((I - LR) * N + (J - LC))
 *
 * where:
 * - B  = Base address
 * - W  = Size of one element in bytes
 * - LR = Lower row index (0 here)
 * - LC = Lower column index (0 here)
 * - N  = Number of columns
 */
void build_matrix(const char** words, int total_words) {

  size_t total_bytes = (size_t)sizeof(uint8_t) * total_words * total_words;

  pattern_matrix = (uint8_t*)malloc(total_bytes);
  if (pattern_matrix == NULL) {
    printf("CRITICAL ERROR: Failed to allocate memory\n");
    return;
  }
  
  for (int i = 0; i < total_words; i++) {
    for (int j = 0; j < total_words; j++) {
      size_t index = (size_t)i * total_words + j;
      pattern_matrix[index] = compute_pattern(words[i], words[j]);
    }
  }
  printf("Pattern Matrix Generated\n");
}

void free_matrix(void) {
  free(pattern_matrix);
  pattern_matrix = NULL;
}

/**
 * @brief Calculates the Shannon Entropy for all words against the remaining valid targets.
 *
 * @param valid_targets Array of indices representing words that are still possible solutions.
 * @param num_valid     Number of elements in the valid_targets array.
 * @param word_freq     Array of float probabilities representing real-world usage frequency.
 * @param total_words   Total number of words in the dictionary (used for matrix offset).
 * @param out_entropy   Pre-allocated array where the calculated entropy scores will be written.
 *
 * @details
 * This function determines the information value of every possible guess. In Information Theory, 
 * a "good" guess is one that evenly shatters the remaining possible targets into as many different 
 * patterns as possible.
 *
 * **The Role of Frequency (Weighting):**
 * Instead of just counting raw words, we sum the real-world probability of those words. 
 * This ensures the algorithm prioritizes splitting up common words (which are highly likely 
 * to be the answer) rather than perfectly dividing obscure, invalid words.
 *
 * **Standard Mode vs. Hard Mode:**
 * The outer loop evaluates all `total_words` rather than just `num_valid` words. This represents 
 * "Standard Mode" optimal play. Guessing a word we know is wrong can often yield a higher 
 * entropy/information gain to escape traps (e.g., guessing "FLIMS" to solve an "_IGHT" trap) 
 * compared to strictly guessing from the remaining valid pool (Hard Mode).
 * * **Performance:**
 * Because it leverages the precomputed `pattern_matrix` LUT, the inner loop requires zero string 
 * comparisons. It executes using strictly O(1) memory lookups and basic float arithmetic.
 */
void calculate_entropies(const int* valid_targets, int num_valid, const float* word_freq, int total_words, float* out_entropy) {

  float total_weight = 0; //Total weight is constant, it is the sum of weights of all valid targets
  for (int i = 0; i < num_valid; i++) {
      int target_idx = valid_targets[i];
      total_weight += word_freq[target_idx];
    }
  
  for(int guess_idx = 0; guess_idx < total_words; guess_idx++) { //For hard mode, loop over valid words only, target words are the only possible guess words
    float pattern_weight[TOTAL_PATTERNS] = {0};

    for (int i = 0; i < num_valid; i++) { //if a target word matches a pattern, it adds the frequency of the word to the pattern as weight
      int target_idx = valid_targets[i];
      size_t pattern_index = (size_t)guess_idx * total_words + target_idx;
      uint8_t pattern = pattern_matrix[pattern_index];
      pattern_weight[pattern] += word_freq[target_idx];
    }

    float entropy = 0; //calculates entropy by using a frequency of the word as weight
    if (total_weight > 0.0f) {
      for (int i = 0; i < TOTAL_PATTERNS; i++) {
        if (pattern_weight[i] > 0.0f) {
          float probablity = pattern_weight[i] / total_weight;
          entropy -= probablity * log2f(probablity);
        }
      }
    }
    out_entropy[guess_idx] = entropy;
  }
}

/**
 * @brief Filters the word pool to find an updated list of possible answers after a guess.
 *
 * @param guess_idx          Index of the guessed word.
 * @param obtained_pattern   The Base-3 integer pattern returned by the game.
 * @param current_valid      Array of indices representing the currently valid target words.
 * @param num_current_valid  Number of elements in the current_valid array.
 * @param total_words        Total number of words in the dictionary (used for matrix offset).
 * @param output_valid       Pre-allocated array to store the indices of the surviving target words.
 * @return int               The number of possible solutions remaining (match count).
 *
 * @details
 * After each guess, we need to filter the word pool to find a list of updated target words, 
 * i.e., possible answers. The current list of valid words is taken as input. Then, using 
 * the current guess word and the obtained pattern, the expected pattern of each word in the 
 * target pool is checked against the obtained pattern. 
 * * If the patterns match, then this word is a possible solution for the next round and is 
 * saved to the output array; otherwise, it is eliminated. The Match Count is tracked and 
 * returned to show exactly how many possible solutions remain.
 */
int filter_words(int guess_idx, uint8_t obtained_pattern, const int* current_valid, int num_current_valid, int total_words, int* output_valid) {
  int match_count = 0;

  for (int i = 0; i < num_current_valid; i++) {
    int target_idx = current_valid[i];
    size_t pattern_index = (size_t)guess_idx * total_words + target_idx;
    uint8_t expected_pattern = pattern_matrix[pattern_index];

    if (obtained_pattern == expected_pattern) {
      output_valid[match_count++] = target_idx;
    }
  }

  return match_count;
}

// gcc -O3 -shared -fPIC -o wordle_engine.so wordle_engine.c -lm
// gcc -O3 -shared -fPIC -fopenmp -o wordle_engine.so wordle_engine.c -lm