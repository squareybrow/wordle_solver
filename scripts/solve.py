from collections import Counter
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# File Paths
data_path = Path(__file__).parent.parent.joinpath('data')
ans_input_dir = data_path.joinpath('word_frequencies.csv')

# Word length constraint
WORD_LEN = 5

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
                entropy -=  probability * np.log2(probability)
        
        entropy_list.append((guess_word, entropy))

    df = pd.DataFrame(entropy_list, columns=['GuessWord', 'Entropy'])
    df['Frequency'] = df['GuessWord'].map(word_freq)
    df = df.sort_values(by=['Entropy', 'Frequency'], ascending=[False, False])
    return df


def filter_words(guess_words, word_freq, guessed_word, pattern_obtained):
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
    guess_words = [word for word in guess_words if calculate_pattern(guessed_word, word) == pattern_obtained]
    new_df = calculate_entropy(guess_words, word_freq)
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

def test_bench(df : pd.DataFrame, word_freq, test_word : str) -> int:
    
    turn = 1
    
    while(True):
        guess = df['GuessWord'].iloc[0]
        
        if guess == test_word:
            print(f'Guessed: {test_word} in {turn} turn(s)')
            break
        
        pattern_obtained = calculate_pattern(guess, test_word)
        df = filter_words(df['GuessWord'], word_freq, guess, pattern_obtained)
        
        if len(df) == 0:
            print(f'Word "{test_word}" not reachable from word list')
            return -1
        
        if (turn >= 100 and guess != test_word):
            print('Unexpected error...Exiting...')
            exit()
            
        turn += 1
    return turn

def debug_compare(guess_word, word_freq):
    pattern_count = Counter()
    pattern_weight = Counter()
    
    for word in guess_word:
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
    
    df = pd.read_csv(data_path.joinpath('entropy_freq.csv'))
    initial_guess = df['GuessWord'][0]
    print(f'Opening Word with highest entropy is: {initial_guess}')
    
    # Test Bench: A test word that acts as the Wordle solution
    
    # test_word = 'glint'.lower()
    # print(test_bench(df, test_word))

    # Manual Mode to solve wordle (Enter G -> Green; Y -> Yellow; ? -> Gray)
    
    # turn = 1
    
    # while True:   
    #     print(f'Turn {turn}: ')
    #     pattern = []
    #     pattern_input = list(input('Enter Pattern you see: '))  # G -> Green; Y -> Yellow; ? -> Gray
    #     for i in pattern_input:
    #         if i == 'G':
    #             pattern.append(0)
    #         elif i == 'Y':
    #             pattern.append(1)
    #         else:
    #             pattern.append(2)
    #     guess = input('Enter word entered: ').lower()
    #     pattern = tuple(pattern)
    #     df= filter_words(df['GuessWord'], word_freq, guess, pattern)
    #     print(f'Remaining Words: {len(df)}')
    #     print(df)
    #     display_pattern(guess, pattern)
    #     print(f"Guess with the highest entropy is: {df['GuessWord'].iloc[0]}")
    #     turn += 1
        
    #     if pattern_input == ['G', 'G', 'G', 'G', 'G']:
    #         print('Wordle Solved!')
    #         print('Exiting...')
    #         break
    
    # Plotting metrics and detailed test
    
    turn_list = []
    df_original = df.copy()
    ans_words = df_guess['Word'].to_list()
    for word in tqdm(ans_words):
        df_copy = df_original.copy()
        turn_list.append(test_bench(df_copy, word_freq, word))
    
    # Unweighted stats (for comparison with old solver)
    mean_turns = float(np.mean(turn_list))
    median_turns = float(np.median(turn_list))
    max_turns = np.max(turn_list)

    # Weighted stats (the proper metric for a frequency-weighted solver)
    weights = np.array([word_freq[w] for w in ans_words])
    weighted_mean = float(np.average(turn_list, weights=weights))

    print('Statistics: ')
    print(f'Unweighted Mean turns: {mean_turns:.2f}')
    print(f'Weighted Mean turns:   {weighted_mean:.2f}')
    print(f'Median turns: {median_turns}')
    print(f'Total Words tested: {len(turn_list)}')
    
    plt.figure(figsize=(10, 6))
    sns.histplot(turn_list, bins=range(1, max_turns + 2), discrete=True, kde=False)
    plt.axvline(mean_turns, color='red', linestyle='--', label=f'Mean = {mean_turns:.02f}')
    plt.axvline(median_turns, color='green', linestyle='--', label=f'Median = {median_turns:.02f}')
    plt.xlabel('No. of Turns to Solve')
    plt.ylabel('No. of Words')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(data_path.joinpath("wordle_weighted_benchmark.png"))
    
    results_df = pd.DataFrame({
        'Word': ans_words,
        'Turns': turn_list
    }).sort_values('Turns', ascending=False)

    print("\nHardest words to solve:")
    print(results_df.head(20))

    print("\nEasiest words to solve:")
    print(results_df.tail(20))

if __name__ == '__main__':
    main()

