from pathlib import Path
from wordfreq import zipf_frequency
import pandas as pd

data_path = Path(__file__).parent.parent.joinpath('data')
DIR_input = data_path.joinpath('all_words.txt')

def main():
    with open(DIR_input, 'r') as file:
        wordle_words = {line.strip().lower() for line in file}
        
    word_list = []
    
    for word in wordle_words:
        zipf = zipf_frequency(word, 'en')
        word_freq = 10**zipf
        word_list.append([word, word_freq])
        
    freq_sum = 0        
    for data in word_list:
        freq_sum += data[1]

    for data in word_list:
        data[1] /= freq_sum

    df = pd.DataFrame(word_list, columns=['Word', 'Frequency'])
    df.to_csv(data_path.joinpath('word_frequencies.csv'), index=False)
    print(df)
    
    
if __name__ == '__main__':
    main()