# Wordle Solver

An entropy-based Wordle solver using information theory.

## How It Works

Uses Shannon entropy to pick optimal guesses that maximize expected information gain.

## Usage

```zsh
python wordle_solver/scripts/solve.py
```

## Files

| File | Purpose |
|------|---------|
| `scripts/solve.py` | Main solver |
| `data/all_words.txt` | Word list (12,973 words) |
| `data/entropy.csv` | Precomputed opening entropies |

## Installation

```zsh
git clone https://github.com/squareybrow/wordle_solver.git
cd wordle_solver
pip install -r requirements.txt
```

## Features
- Finds optimal starting word using entropy
- Solves any Wordle word automatically
- Manual mode for interactive solving
- Colorful terminal output
- Generates statistics and histograms
- Lists hardest and easiest words to solve

## Inspiration

[3Blue1Brown - Solving Wordle using Information Theory](https://youtu.be/v68zYyaEmEA)

For a detailed explanation of the algorithm, results and development process, see the [devlog](docs/devlog.md).