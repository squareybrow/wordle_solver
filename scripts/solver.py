"""
    This Script uses a C program in form of a Shared Library, it loads words, frequencies into C, so the calculation is faster.
    For stuff C is not so great at, like data visualisation, taking user input, File I/O processing, 
    this script is used to handle those tasks.
"""
import ctypes
import pandas as pd
from pathlib import Path
import time

start_time = time.time()

# Define base and wordlen here, in case you ever want to solve a 10 letter wordle
BASE = 3
WORDLEN = 5

# Loading the data (list of words and frequencies)
data_path = Path(__file__).parent.parent.joinpath('data')
input_path = data_path.joinpath('word_frequencies.csv')

# Loading the C Library
lib_path = Path(__file__).parent.joinpath('wordle_engine.so')
lib = ctypes.CDLL(str(lib_path))

# Defining args and res types for the C functions

# void build_matrix(const char** words, int total_words)
lib.build_matrix.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]

# void free_matrix(void)
lib.free_matrix.argtypes = []
lib.free_matrix.restype = None

# void calculate_entropies(const int* valid_targets, int num_valid, const float* word_freq, int total_words, float* out_entropy)
lib.calculate_entropies.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
lib.calculate_entropies.restype = None

# int filter_words(int guess_idx, uint8_t obtained_pattern, const int* current_valid, int num_current_valid, int total_words, int* output_valid) {
lib.filter_words.argtypes = [ctypes.c_int, ctypes.c_uint8, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
lib.filter_words.restype = ctypes.c_int

print(f'C Engine initialised in {time.time() - start_time}s')

def pattern_to_int(pattern_str: str) -> int:
    mapping = {'G' : 0, 'Y' : 1, '?' : 2}
    pattern_val = 0
    
    for char in pattern_str:
        pattern_val = (pattern_val * BASE) + mapping.get(char, 2) # Using Horner's Method here, same as in the C function compute_pattern
        
    return pattern_val

def display_pattern(guess_word: str, pattern_str: str):
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    GRAY = '\033[100m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    result = ''
    for i, char in enumerate(pattern_str):
        letter = guess_word[i].upper()
        if char == 'G':
            result += f'{GREEN}{WHITE} {letter} {RESET}'
        elif char == 'Y':
            result += f'{YELLOW}{WHITE} {letter} {RESET}'
        else:
            result += f'{GRAY}{WHITE} {letter} {RESET}'
    print(result)
    
    
def main():
    df = pd.read_csv(input_path)
    word_list = df['Word'].to_list()
    freq_list = df['Frequency'].to_list()
    total_words = len(word_list)
    
    c_words_array = (ctypes.c_char_p * total_words)()
    for i, word in enumerate(word_list):
        c_words_array[i] = word.encode('utf-8')
    
    c_frequency_array = (ctypes.c_float * total_words)(*freq_list)
    
    print('Building Matrix...')
    
    lib.build_matrix(c_words_array, total_words)
    
    print(f'Pattern Matrix built in {time.time() - start_time}s')
    
    valid_targets = (ctypes.c_int * total_words)(*range(total_words))
    num_valid = total_words
    output_valid = (ctypes.c_int * total_words)(*range(total_words))
    out_entropy = (ctypes.c_float * total_words)()
    
    turn = 1
    while True:
        loop_time = time.time()
        lib.calculate_entropies(valid_targets, num_valid, c_frequency_array, total_words, out_entropy)
        print(f'Entropy for Turn {turn} calculated in {time.time() - loop_time}s')
        
        valid_set = set(valid_targets[:num_valid]) # Create a set of first num_valid entries in valid_targets
        
        results = []
        for i in range(total_words):
            isValid = 1 if i in valid_set else 0
            results.append((word_list[i], out_entropy[i], freq_list[i], isValid))
            
        df_results = pd.DataFrame(results, columns=['GuessWord', 'Entropy', 'Frequency', 'isValid'])
        df_results = df_results.sort_values(by=['Entropy', 'isValid' ,'Frequency'], ascending=[False, False, False])
        
        print(f'Remaining Words: {num_valid}')
        print('Top 10 Guesses')
        print(df_results[['GuessWord', 'Entropy', 'Frequency']].head())
        
        best_word = df_results.iloc[0]['GuessWord']
        print(f'\nTurn: {turn} | Suggested Word: {best_word.upper()} | Remaining : {num_valid}')
        pattern_input = input('Enter Pattern (G/Y/?): ').upper().strip()
        display_pattern(best_word, pattern_input)
        
        guess_input = input(f'Word you typed (Enter = {best_word}): ').strip().lower()
        guess_input = guess_input if guess_input else best_word
        guess_idx = word_list.index(guess_input)
        
        pattern_int = pattern_to_int(pattern_input)
        num_valid = lib.filter_words(guess_idx, pattern_int, valid_targets, num_valid, total_words, output_valid)
        valid_targets = (ctypes.c_int * num_valid)(*output_valid[:num_valid])
        
        if pattern_input == 'GGGGG':
            print(f'Wordle Solved in {turn} turn(s)')
            print('Exiting...')
            break
        
        if num_valid == 0:
            print('No remaining words, consider rechecking pattern input')
            break
        
        turn += 1
        
    lib.free_matrix()
    
if __name__ == '__main__':
    main()