import ctypes
from pathlib import Path
import pandas as pd

BASE = 3
WORDLEN = 5

data_path = Path(__file__).parent.parent.joinpath('data')
input_dir = data_path.joinpath('word_frequencies.csv')

lib_path = Path(__file__).parent.joinpath('wordle_engine.so')
lib = ctypes.CDLL(str(lib_path))

# void build_matrix(const char** words, int total_words)
lib.build_matrix.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
lib.build_matrix.restype = None

# void free_matrix(void)
lib.free_matrix.argtypes = []
lib.free_matrix.restype = None

# void calculate_entropies(const int* valid_targets, int num_valid, const float* word_freq, int total_words, float* out_entropy)
lib.calculate_entropies.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
lib.calculate_entropies.restype = None

# int filter_words(int guess_idx, uint8_t obtained_pattern, const int* current_valid, int num_current_valid, int total_words, int* output_valid) {
lib.filter_words.argtypes = [ctypes.c_int, ctypes.c_uint8, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
lib.filter_words.restype = ctypes.c_int

print('C Engine Loaded')

def pattern_to_int(pattern_str: str) -> int:
    mapping = {'G' : 0, 'Y': 1, '?': 2}
    pattern_val = 0
    
    for char in pattern_str:
        pattern_val = (pattern_val * BASE) + mapping.get(char, 2)
        
    return pattern_val

def display_pattern(guess_word, pattern_str):
    """Displays a Wordle-like colorful output using ANSI color codes."""
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
    df = pd.read_csv(input_dir)
    words_list = df['Word'].to_list()
    freq_list = df['Frequency'].to_list()
    total_words = len(words_list)
    
    c_words_array = (ctypes.c_char_p * total_words)()
    for i, word in enumerate(words_list):
        c_words_array[i] = word.encode('utf-8')
        
    c_freqs_array = (ctypes.c_float * total_words)(*freq_list)
    
    print('Building Matrix...')
    lib.build_matrix(c_words_array, total_words)
    
    
    num_valid = total_words
    valid_targets = (ctypes.c_int * total_words)(*range(total_words))
    output_valid = (ctypes.c_int * total_words)()
    out_entropy = (ctypes.c_float * total_words)()
    
    turn  = 1
    while True:
        lib.calculate_entropies(valid_targets, num_valid, c_freqs_array, total_words, out_entropy)
        
        # --- THE FIX STARTS HERE ---
        # 1. Convert the C array into a Python set for instant lookups
        valid_set = set(valid_targets[:num_valid])
        
        # 2. Build the results list with a new 'IsValid' flag
        results = []
        for i in range(total_words):
            # Flag if the word is actually a possible answer (1) or not (0)
            is_valid = 1 if i in valid_set else 0
            results.append((words_list[i], out_entropy[i], is_valid, freq_list[i]))
            
        df_results = pd.DataFrame(results, columns=['GuessWord', 'Entropy', 'IsValid', 'Frequency'])
        
        # 3. Sort by Entropy FIRST, then prioritize Valid Words, then Frequency
        df_results = df_results.sort_values(by=['Entropy', 'IsValid', 'Frequency'], ascending=[False, False, False])
        # --- THE FIX ENDS HERE ---
        
        print(f'Remaining Words: {num_valid}')
        print("Top 10 Guesses:")
        # Hide the IsValid column just to keep your terminal output clean
        print(df_results[['GuessWord', 'Entropy', 'Frequency']].head(10))
        
        best_word = df_results.iloc[0]['GuessWord']
        print(f'\nTurn {turn} | Suggested: {best_word.upper()} | Remaining: {num_valid}')
        
        pattern_input = input('Enter Pattern (G/Y/?): ').upper().strip()
        display_pattern(best_word, pattern_input)
        
        if pattern_input == 'GGGGG':
            print(f'Wordle Solved in {turn} turn(s)!')
            break
        
        guess_input = input(f'Word you typed (Enter = {best_word}): ').strip().lower()
        guess_word = guess_input if guess_input else best_word
        guess_idx = words_list.index(guess_word)

        pattern_int = pattern_to_int(pattern_input)
        num_valid = lib.filter_words(guess_idx, pattern_int, valid_targets, num_valid, total_words, output_valid)
        valid_targets = (ctypes.c_int * num_valid)(*output_valid[:num_valid])

        if num_valid == 0:
            print('No words remaining — check pattern input.')
            break

        turn += 1
    
    lib.free_matrix()
    
if __name__ == '__main__':
    main()