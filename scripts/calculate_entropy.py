from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import Counter

WORD_LEN = 5

data_path = Path(__file__).parent.parent.joinpath('data')
guess_input_dir = data_path.joinpath('all_words.txt')
ans_input_dir = data_path.joinpath('word_frequencies.csv')

def calculate_pattern(guess_word : str, actual_word : str) -> tuple:
    """
    Compares the guess word against the actual target word or previous guess and generates a 
    Wordle-like pattern, where 0 -> Green; 1 -> Yellow; 2 -> Gray
    """
    
    wrong = []
    # 0 -> Green; 1 -> Yellow; 2 -> Gray
    pattern = [0] * WORD_LEN
    
    wrong = [i for i, v in enumerate(guess_word) if v != actual_word[i]]
    missed_letter_count = Counter(actual_word[i] for i in wrong)
    
    # Handle yellow letters: checks if a letter is used but not in the correct position
    # Assigns code 1 if present elsewhere, or code 2 if not present at all
    for i in wrong:
        v = guess_word[i]
        if missed_letter_count[v] > 0:
            pattern[i] = 1
            missed_letter_count[v] -= 1
        else:
            pattern[i] = 2
    return tuple(pattern)

def calculate_entropy(guess_words, word_freq, show_progress=False):
    """
    Calculates the entropy of each word in the list against all other words.
    Uses tqdm to provide a progress bar to measure the completion rate of the operation.

    Args:
        words (list): A list of words from the main file or from DataFrames formed while filtering words
        entropy_list (list): Stores a tuple of the input word and its measured entropy

    Returns:
        pandas.DataFrame: Contains a table of words and their calculated entropy in descending order
    """
    entropy_list = []
    iterator = tqdm(guess_words) if show_progress else guess_words
    for guess_word in iterator:
        pattern_weight = Counter()
        for word in guess_words:
            pattern = calculate_pattern(guess_word, word)
            pattern_weight[pattern] += word_freq[word]
             
        entropy = 0
        total_weight = sum(pattern_weight.values())
        for pattern in pattern_weight:
            
            # Shannon Entropy Calculation
            probability = (pattern_weight[pattern] / total_weight)
            if probability > 0:
                entropy +=  probability * np.log2(1 / probability)
        
        entropy_list.append((guess_word, entropy))

    df = pd.DataFrame(entropy_list, columns=['GuessWord', 'Entropy']).sort_values(by='Entropy', ascending=False)
    return df

def debug_compare(guess_word, ans_word, word_freq):
    pattern_count = Counter()
    pattern_weight = Counter()
    
    for word in ans_word:
        pattern = calculate_pattern(guess_word, word)
        pattern_count[pattern] += 1
        pattern_weight[pattern] += word_freq[word]
    
    print(f'\n=== {guess_word.upper()} ===')
    print(f'{'Pattern':<20} {'Count':>8} {'Weight':>10}')
    for pattern in sorted(pattern_count.keys(), key=lambda p: pattern_count[p], reverse=True)[:10]:
        print(f"{str(pattern):<20} {pattern_count[pattern]:>8} {pattern_weight[pattern]:>10.6f}")

def main():
    df_guess = pd.read_csv(ans_input_dir)
    word_freq = dict(zip(df_guess['Word'], df_guess['Frequency']))
    
    
    df = calculate_entropy(df_guess['Word'], word_freq, True)
    df.to_csv(data_path.joinpath('entropy_freq.csv'), index=False)
    print(df)
    
    
    # debug_compare('crane', df_ans['Word'], word_freq)
    # debug_compare('slate', df_ans['Word'], word_freq)
    # debug_compare('jills', df_ans['Word'], word_freq)
    
if __name__ == '__main__':
    main()