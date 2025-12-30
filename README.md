# Wordle Solver

An entropy-based Wordle solver using information theory.

## TL;DR
Built an entropy-based Wordle solver inspired by information theory. 
Achieves **median solve in 4 turns**, **mean of 4.58 turns** across all 
12,973 possible words.

**Quick Links:** [Results](#results) • [How It Works](#my-approach) • [Hardest/Easiest Words](#hardest-and-easiest-words-to-solve) • [Installation](#installation)

---

## The Story

I regularly play Wordle. I had just finished my 3rd semester, quite bored at home, and hadn't been able to guess the Wordle word of the day for 3 days straight! Needless to say, I was kinda frustrated. I was browsing YouTube when I came across the above-mentioned 3Blue1Brown video where he talks about using entropy to solve puzzles such as... wait for it... Wordle!

Now, here I am bored, haven't been able to solve Wordle for 3 days, just had a semester-long class on random variables, and also needed to practice some programming. What more reason do I need? And that's how I started working on this script to solve Wordle puzzles using information theory.

---

## What is Wordle?

Wordle is a fun word game where you need to guess the word of the day, which is a five-letter word. If you guess wrong, you get hints:

- **Green** — The letter is present in the word and in the correct position
- **Yellow** — The letter is present in the word but not in the correct position  
- **Gray** — The letter is not present in the word at all

The official Wordle word list contains 12,973 accepted words. That's a huge list! How do we even figure out which word is best to start with? Can we somehow quantify the amount of information each word gives us? How do we measure the quality of a guess?

---

## Measuring Information

Information is measured in bits (*I*), where:

$$I = \log_2\left(\frac{1}{p(x)}\right)$$

Here, *p(x)* is the probability of the event occurring. For example, in English, about half of the five-letter words contain the letter 's'. So, this observation gives us around 1 bit of information. If a letter is present in about a quarter of the five-letter words, it gives $\log_2(4) = 2$ bits. A probability of 1/8 gives 3 bits, and so on.

![Image demonstrating Information in terms of Bits](docs/image.png)

This method of measuring information is especially nice in the context of words, since saying an event has 20 bits of information is much easier than saying it has a probability of 0.00000095. But the best part is that information **adds together**: if one event gives you 3 bits and another gives you 2 bits, and they're independent, then $I_{\text{total}} = I_1 + I_2$.

---

## Entropy and the Bot

The goal here is to design a Wordle bot that uses this information to solve the puzzle. Specifically, I'm using **entropy**, as developed by Claude Shannon.

Entropy is a measure of the "flatness" of a distribution, or the amount of randomness present in the data, i.e., how much information it holds.

Formally:

$$E[I] = \sum p(x) \times \log_2\left(\frac{1}{p(x)}\right)$$

---

## My Approach

### Step 1: Find the Best Starting Word

The first step was to find a word that would eliminate the most possible candidates—in other words, the word with the most information (maximum entropy).

- A function was written to calculate the Wordle pattern: 0 → Green, 1 → Yellow, 2 → Gray
- A list of all possible patterns was made (for five letters and three colors, that's $3^5 = 243$ patterns)
- For each word, the pattern it would produce with every other word was calculated
- The frequency of each pattern was counted and the probability of each pattern was calculated
- Using the entropy formula, the information content for each word was computed
- This was repeated for every word in the list (takes a long time to compute!)
- Finally, the entropy values for each word were saved in a pandas DataFrame and exported as a CSV for later use. Since the opening word's entropy is always the same, we can just compute it once and use it. This saves a ton of computation time.

### Step 2: Guessing and Filtering

At this point, I have the opening word, and functions to calculate the pattern and entropy.

- After entering the opening word, the pattern was checked against the target word
- The word list was filtered to keep only those words that matched the pattern
- Entropy was recalculated for the filtered list
- The word with the highest entropy became the next guess
- This process repeated for up to 6 steps or until the puzzle was solved

---

## Results

The success rate is quite good! However, I noticed that for the word **'loved'**, it required 7 steps, which means it failed the Wordle game (since you only get 6 attempts).

![Log of the word 'loved' failing the puzzle](docs/image-1.png)

But for most words, the bot does really well:

![Log of the bot solving for 'conch'](docs/image-3.png)
![Log of the bot solving for 'honda'](docs/image-2.png)

We can also solve for the word manually:

![Log of bot solving Wordle manually for the word 'spool'](docs/image-4.png)

---

Seeing mixed results, I naturally wanted to calculate the statistics of my puzzle solver.

For a definitive test, I used every word as a test word to quantify the median and average number of turns required to solve the puzzle. 
After running all 12,973 words (which took quite some time, blame my spaghetti code), I generated a histogram for the number of turns required.

![Benchmark results](data/wordle_benchmark.png)

As seen from the results, the **median number of turns required was 4**.
The **mean number of turns was 4.58**.

---

## Hardest and Easiest Words to Solve

Based on the benchmark results, I identified both the hardest and easiest words for the solver:

### Hardest Words to Solve

| #    | Word   | Turns |
|------|--------|-------|
| 7431 | yills  | 17    |
| 4574 | jills  | 16    |
| 11491| vills  | 15    |
| 12448| karks  | 15    |
| 435  | yells  | 14    |
| 3842 | jarks  | 14    |
| 9645 | jests  | 14    |
| 8951 | cills  | 14    |
| 11377| rares  | 14    |
| 5985 | vangs  | 14    |
| 6643 | rarks  | 13    |
| 195  | vares  | 13    |
| 5503 | kores  | 13    |
| 2535 | bells  | 13    |
| 11507| years  | 13    |
| 11558| zests  | 13    |
| 303  | zills  | 13    |
| 11119| eales  | 13    |
| 9530 | zeals  | 13    |
| 7032 | yangs  | 13    |

### Easiest Words to Solve

| #    | Word   | Turns |
|------|--------|-------|
| 1146 | terce  | 2     |
| 967  | lions  | 2     |
| 12934| curio  | 2     |
| 903  | twain  | 2     |
| 392  | ester  | 2     |
| 842  | yores  | 2     |
| 802  | ratha  | 2     |
| 753  | spaer  | 2     |
| 728  | sepal  | 2     |
| 711  | nerts  | 2     |
| 590  | orant  | 2     |
| 534  | haint  | 2     |
| 206  | serai  | 2     |
| 350  | terns  | 2     |
| 342  | retie  | 2     |
| 245  | grail  | 2     |
| 111  | tasar  | 2     |
| 139  | regie  | 2     |
| 39   | grabs  | 2     |
| 7566 | tares  | 1     |

---

## Installation

```zsh
git clone https://github.com/squareybrow/wordle_solver.git
cd wordle_solver
pip install -r requirements.txt
```

## Usage

```zsh
python wordle_solver/scripts/solve.py
```

## Features
- Finds optimal starting word using entropy
- Solves any Wordle word automatically
- Manual mode for interactive solving
- Colorful terminal output
- Generates statistics and histograms
- Lists hardest and easiest words to solve

## Files

| File | Purpose |
|------|---------|
| `scripts/solve.py` | Main solver |
| `data/all_words.txt` | Word list (12,973 words) |
| `data/entropy.csv` | Precomputed opening entropies |

---

## Possible Solution Ideas

One potential improvement is to incorporate word frequency data from sources such as Wikipedia. Since Wordle typically selects common words as solutions, weighting these words more heavily could help the bot prioritize likely answers and avoid obscure guesses.

---

## What's Next?

Recently completed:
- Visualized the distribution of guessed words with additional histograms.
- Developed a "manual mode" to assist with solving Wordle interactively.

Planned improvements:
- Experiment with the frequency-based approach described above.
- Refactor the codebase, possibly separating scripts or porting the project to C or C++ for further learning.

---

## Inspiration

[3Blue1Brown - Solving Wordle using Information Theory](https://youtu.be/v68zYyaEmEA)