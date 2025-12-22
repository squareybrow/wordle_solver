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

## Requirements

```zsh
pip install -r requirements.txt
```

## Inspiration

[3Blue1Brown - Solving Wordle using Information Theory](https://youtu.be/v68zYyaEmEA)

For a detailed explanation of the algorithm and development process, see the [devlog](docs/devlog.md).