"""
    This Script uses a C program in form of a Shared Library, it loads words, frequencies into C, so the calculation is faster.
    For stuff C is not so great at, like data visualisation, taking user input, File I/O processing, 
    this script is used to handle those tasks.
"""
import ctypes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from pathlib import Path
import time

start_time = time.time()

# Define base and wordlen here, in case you ever want to solve a 10 letter wordle
BASE = 3
WORDLEN = 5
RUN_BENCHMARK = False # To toggle manual mode or benchmark mode

# Loading the data (list of words and frequencies)
data_path = Path(__file__).parent.parent.joinpath('data')
input_path = data_path.joinpath('word_frequencies.csv')

# Loading the C Library
lib_path = Path(__file__).parent.joinpath('wordle_engine.so')
lib = ctypes.CDLL(str(lib_path))

# Defining args and res types for the C functions

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

# uint8_t get_matrix_pattern(int guess_idx, int target_idx, int total_words)
lib.get_matrix_pattern.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.get_matrix_pattern.restype = ctypes.c_uint8

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
    
def simulate_game(test_word, total_words, c_frequency_array, freq_list, word_list):  
    valid_targets = (ctypes.c_int * total_words)(*range(total_words))
    num_valid = total_words
    output_valid = (ctypes.c_int * total_words)(*range(total_words))
    out_entropy = (ctypes.c_float * total_words)()
    
    test_word_idx = word_list.index(test_word)
    
    for turn in  range(1, 20):
        lib.calculate_entropies(valid_targets, num_valid, c_frequency_array, total_words, out_entropy)
        
        valid_set = set(valid_targets[:num_valid]) # Create a set of first num_valid entries in valid_targets
        best_guess_idx = max(
            range(total_words),
            key=lambda i: (out_entropy[i], 1 if i in valid_set else 0, freq_list[i])
        )
        
        pattern_int = lib.get_matrix_pattern(best_guess_idx, test_word_idx, total_words)
        
        if pattern_int == 0:
            return turn
        
        num_valid = lib.filter_words(best_guess_idx, pattern_int, valid_targets, num_valid, total_words, output_valid)
        valid_targets = (ctypes.c_int * num_valid)(*output_valid[:num_valid])
        
        if num_valid == 0:
            return -1 
        
    return -1
        
def run_benchmark(ans_words, total_words, c_frequency_array, freq_list, word_list):
    
    print(f'Starting Automated Benchmark with {len(ans_words)} Test Words')
    turn_list = []
    for test_word in tqdm(ans_words, desc="Benchmarking Words"):
        turn_list.append(simulate_game(test_word, total_words, c_frequency_array, freq_list, word_list))
        
    mean_turns    = float(np.mean(turn_list))
    median_turns  = float(np.median(turn_list))
    max_turns     = int(np.max(turn_list))
    win_rate      = sum(1 for t in turn_list if 0 < t <= 6) / len(turn_list) * 100
    weights       = np.array([freq_list[word_list.index(w)] for w in ans_words])
    weighted_mean = float(np.average(turn_list, weights=weights))
        
    print('Statistics: ')
    print(f"  Total Words Tested : {len(turn_list)}")
    print(f"  Win Rate (≤6)      : {win_rate:.1f}%")
    print(f"  Unweighted Mean    : {mean_turns:.4f}")
    print(f"  Weighted Mean      : {weighted_mean:.4f}")
    print(f"  Median             : {median_turns:.0f}")
    print(f"  Max Turns          : {max_turns}")
    
    
    # Lines 137 - 183 have been written with help of AI 
    
    # 1. Configure Seaborn for a custom, modern dark theme
    sns.set_theme(style="darkgrid", rc={
        "axes.facecolor": "#1e1e1e",      # Dark grey plot background
        "figure.facecolor": "#121212",    # Almost black figure background
        "grid.color": "#333333",          # Subtle grid lines
        "text.color": "#e0e0e0",          # Off-white text
        "axes.labelcolor": "#e0e0e0",     # Off-white axis labels
        "xtick.color": "#e0e0e0",         # Off-white tick marks
        "ytick.color": "#e0e0e0"
    })
    
    plt.figure(figsize=(10, 6))
    
    # 2. Use a vibrant, slightly translucent blue for the bars
    ax = sns.histplot(turn_list, bins=range(1, max_turns + 2), discrete=True, kde=False, 
                      color="#4A90E2", edgecolor="#121212", alpha=0.9)

    # 3. Swap to high-contrast, bright "neon" colors for the statistics
    plt.axvline(mean_turns, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Mean = {mean_turns:.02f}')
    plt.axvline(median_turns, color='#2ED573', linestyle=':', linewidth=2, label=f'Median = {median_turns:.02f}')
    plt.axvline(weighted_mean, color='#FFA502', linestyle='-.', linewidth=2, label=f'Weighted Mean = {weighted_mean:.02f}')
    
    # 4. Add Title and upgrade the axis labels
    plt.title('Wordle Solver Performance Benchmark', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Number of Turns to Solve', fontsize=12)
    plt.ylabel('Number of Words', fontsize=12)
    
    # 5. Force the x-axis to only show whole numbers
    plt.xticks(range(1, max_turns + 1))
    
    # 6. Adjust the text box to match the dark theme
    plt.text(0.95, 0.5, f'Win Rate (≤6): {win_rate:.1f}%', 
             transform=ax.transAxes, fontsize=12, horizontalalignment='right', color="#e0e0e0",
             bbox=dict(facecolor='#2d2d2d', alpha=0.9, edgecolor='#444444', boxstyle='round,pad=0.5'))

    # 7. Darken the legend box
    legend = plt.legend(frameon=True, shadow=True, borderpad=1)
    legend.get_frame().set_facecolor('#2d2d2d')
    legend.get_frame().set_edgecolor('#444444')
    for text in legend.get_texts():
        text.set_color('#e0e0e0')
    
    sns.despine(left=True, bottom=True) 
    
    plt.tight_layout()
    
    # 8. CRITICAL: Force the facecolor when saving, otherwise Matplotlib might default to a transparent/white background!
    plt.savefig(data_path.joinpath("wordle_weighted_benchmark_dark.png"), dpi=300, facecolor='#121212')
    
    results_df = pd.DataFrame({
        'Word': ans_words,
        'Turns': turn_list
    }).sort_values('Turns', ascending=False)

    print("\nHardest words to solve:")
    print(results_df.head(20))
    
    print("\nEasiest words to solve:")
    print(results_df.tail(20))
        
        
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
    
    if RUN_BENCHMARK:
        print("\n=== ENTERING TESTBENCH MODE ===")
        # Usually you'd load a specific answers list here. For now, testing against all words.
        ans_path = data_path.joinpath('answers.txt')
        ans_words = []
        with open(ans_path, 'r') as file:
            ans_words = sorted([line.strip().lower() for line in file])
        run_benchmark(ans_words, total_words, c_frequency_array, freq_list, word_list)
        
    else:
        print("\n=== ENTERING MANUAL MODE ===")
        valid_targets = (ctypes.c_int * total_words)(*range(total_words))
        num_valid = total_words
        output_valid = (ctypes.c_int * total_words)(*range(total_words))
        out_entropy = (ctypes.c_float * total_words)()
        
        turn = 1
        while True:
            loop_time = time.time()
            lib.calculate_entropies(valid_targets, num_valid, c_frequency_array, total_words, out_entropy)
            print(f'Entropy for Turn {turn} calculated in {time.time() - loop_time:.4f}s')
            
            valid_set = set(valid_targets[:num_valid])
            
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
            
            if pattern_int == 0:
                print(f'Wordle Solved in {turn} turn(s)')
                print('Exiting...')
                break
            
            num_valid = lib.filter_words(guess_idx, pattern_int, valid_targets, num_valid, total_words, output_valid)
            valid_targets = (ctypes.c_int * num_valid)(*output_valid[:num_valid])
            
            if num_valid == 0:
                print('No remaining words, consider rechecking pattern input')
                break
            
            turn += 1
            
    lib.free_matrix()
    
if __name__ == '__main__':
    main()