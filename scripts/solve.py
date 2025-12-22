from collections import Counter
from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm

# File Paths
DIR = 'wordle_solver/data/all_words.txt'
DIR_opening_word = 'wordle_solver/data/entropy.csv'

# Word length constraint
WORD_LEN = 5

def calculate_pattern(guess_word, actual_word):
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

def calculate_entropy(words, entropy_list):
    """
    Calculates the entropy of each word in the list against all other words.
    Uses tqdm to provide a progress bar to measure the completion rate of the operation.

    Args:
        words (list): A list of words from the main file or from DataFrames formed while filtering words
        entropy_list (list): Stores a tuple of the input word and its measured entropy

    Returns:
        pandas.DataFrame: Contains a table of words and their calculated entropy in descending order
    """
    for guess_word in tqdm(words):
        pattern_count = Counter()
        for word in words:
            pattern = calculate_pattern(guess_word, word)
            pattern_count[pattern] += 1
        
        entropy = 0
        total_words = len(words)
        for pattern in pattern_count:
            
            # Shannon Entropy Calculation
            probability = (pattern_count[pattern] / total_words)
            if probability != 0:
                entropy +=  probability * np.log2(1 / probability)
            
        entropy_list.append((guess_word, entropy))

    df = pd.DataFrame(entropy_list, columns=['GuessWord', 'Entropy']).sort_values(by='Entropy', ascending=False)
    return df


def filter_words(df_words, guess_word, pattern_obtained):
    """
    Filters the word list based on the guess word and pattern obtained. Checks all words 
    in the list against the guess word, keeps the words that produce the same pattern, 
    and discards the ones that don't.

    Args:
        df_words (pandas.DataFrame): The 'GuessWord' column of the DataFrame is used as the list input
        guess_word (str): The guess word used in the last iteration
        pattern_obtained (tuple): Pattern formed by checking the current guess word against the target

    Returns:
        pandas.DataFrame: A filtered DataFrame containing only words that match the pattern with recalculated entropy
    """
    guess_words = [word for word in df_words['GuessWord'] if calculate_pattern(guess_word, word) == pattern_obtained]
    entropy_list = []
    new_df = calculate_entropy(guess_words, entropy_list)
    return new_df

def display_pattern(guess_word, pattern):
    """
    Displays a Wordle-like colorful output using ANSI color codes.

    Args:
        guess_word (str): The guess word used
        pattern (tuple): The pattern obtained after checking the current guess word against the target
    """
    # ANSI color codes
    GREEN = '\033[42m'   # Green background
    YELLOW = '\033[43m'  # Yellow background
    GRAY = '\033[100m'   # Gray background
    WHITE = '\033[97m'   # White text
    RESET = '\033[0m'    # Reset colors
    
    result = ''
    for i, code in enumerate(pattern):
        letter = guess_word[i].upper()
        if code == 0:
            result += f'{GREEN}{WHITE} {letter} {RESET}'
        elif code == 1:
            result += f'{YELLOW}{WHITE} {letter} {RESET}'
        else:
            result += f'{GRAY}{WHITE} {letter} {RESET}'
    print(result)

def main():
    with open(DIR, 'r') as file:
        wordle_words = {line.strip().lower() for line in file}

    # calculate_entropy(wordle_words, entropy_words)
    # entropy_words.to_csv('wordle_solver/data/entropy.csv', index=False)

    df = pd.read_csv(DIR_opening_word)
    initial_guess = df['GuessWord'][0]
    print(f'Opening Word with highest entropy is: {initial_guess}')
    
    # Test Bench: A test word that acts as the Wordle solution
    test_word = 'honda'.lower()

    for turn in range(1, 7):
        guess = df['GuessWord'][0]
        print(f'Word guessed in turn {turn} is: {guess}')

        if guess == test_word:
            pattern_obtained = tuple([0] * WORD_LEN)  # All green when guessed correctly
            display_pattern(guess, pattern_obtained)
            print(f'Bot guessed in {turn} turn(s)')
            break
        
        pattern_obtained = calculate_pattern(guess, test_word)
        print(f'Pattern Obtained: {pattern_obtained}')

        df = filter_words(df, guess, pattern_obtained)
        print(f'Remaining Words: {len(df)}')
        
        display_pattern(guess, pattern_obtained)

        if (turn == 6 and guess != test_word):
            print('Couldn\'t guess. Failed to solve')

if __name__ == '__main__':
    main()