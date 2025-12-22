from collections import Counter
from itertools import product
import numpy as np
import pandas as pd
from tqdm import tqdm

DIR = 'wordle_solver/data/all_words.txt'
DIR_opening_word = 'wordle_solver/data/entropy.csv'
WORD_LEN = 5

def calculate_pattern(guess_word, actual_word):
    wrong = []
    # 0 -> Green; 1 -> Yellow; 2 -> Gray
    pattern = [0] * WORD_LEN
    
    wrong = [i for i, v in enumerate(guess_word) if v != actual_word[i]]
    missed_letter_count = Counter(actual_word[i] for i in wrong)
    
    for i in wrong:
        v = guess_word[i]
        if missed_letter_count[v] > 0:
            pattern[i] = 1
            missed_letter_count[v] -= 1
        else:
            pattern[i] = 2
    return tuple(pattern)

def calculate_entropy(words, entropy_list):
    
    for guess_word in tqdm(words):
        pattern_count = Counter()
        for word in words:
            pattern = calculate_pattern(guess_word, word)
            pattern_count[pattern] += 1
        
        entropy = 0
        total_words = len(words)
        for pattern in pattern_count:
            probability = (pattern_count[pattern] / total_words)
            if probability != 0:
                entropy +=  probability * np.log2(1 / probability)
            
        entropy_list.append((guess_word, entropy))

    df = pd.DataFrame(entropy_list, columns=['GuessWord', 'Entropy']).sort_values(by='Entropy', ascending=False)
    return df


def filter_words(df_words, guess_word, pattern_obtained):
    guess_words = [word for word in df_words['GuessWord'] if calculate_pattern(guess_word, word) == pattern_obtained]
    entropy_list = []
    new_df = calculate_entropy(guess_words, entropy_list)
    return new_df

def display_pattern(guess_word, pattern):
    
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
    all_patterns = list(product([0, 1, 2], repeat=WORD_LEN))

    with open(DIR, 'r') as file:
        wordle_words = {line.strip().lower() for line in file}

    # calculate_entropy(wordle_words, entropy_words)
    # entropy_words.to_csv('wordle_solver/data/entropy.csv', index=False)

    df = pd.read_csv(DIR_opening_word)
    initial_guess = df['GuessWord'][0]
    print(f'Opening Word with highest entropy is: {initial_guess}')
    
    test_word = 'honda'.lower()

    for turn in range(1, 7):
        guess = df['GuessWord'][0]
        print(f'Word guessed in turn {turn} is: {guess}')

        if guess == test_word:
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
