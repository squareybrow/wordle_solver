# Wordle Solver Devlog

This project (or reimplementation for the learning experience) was inspired by 3Blue1Brown: [Solving Wordle using Information Theory](https://youtu.be/v68zYyaEmEA?si=lnlih10itb6RYW6Z)

---

## What is Wordle?

Wordle is a fun word game where you need to guess the word of the day, which is a five-letter word. If you guess wrong, you get hints:

- **Green** — The letter is present in the word and in the correct position
- **Yellow** — The letter is present in the word but not in the correct position  
- **Gray** — The letter is not present in the word at all

Wordle provides a list of 12,973 words that are accepted in the puzzle. That's a huge list! How do we even figure out which word is best to start with? Can we somehow quantify the amount of information each word gives us? How do we measure the quality of a guess?

---

## Measuring Information

Information is measured in bits (*I*), where:

$$I = \log_2\left(\frac{1}{p(x)}\right)$$

Here, *p(x)* is the probability of the event occurring. For example, in English, about half of the five-letter words contain the letter 's'. So, this observation gives us around 1 bit of information. If a letter is present in about a quarter of the five-letter words, it gives $\log_2(4) = 2$ bits. A probability of 1/8 gives 3 bits, and so on.

![Image demonstrating Information in terms of Bits](image.png)

This method of measuring information is especially nice in the context of words, since saying an event has 20 bits of information is much easier than saying it has a probability of 0.00000095. But the best part is that information **adds together**: if one event gives you 3 bits and another gives you 2 bits, and they're independent, then $I_{\text{total}} = I_1 + I_2$.

---

## Entropy and the Bot

The goal here is to design a Wordle bot that uses this information to solve the puzzle. Specifically, I'm using **entropy**, as developed by Claude Shannon.

Entropy is a measure of the "flatness" of a distribution, or the amount of randomness present in the data—in other words, how much information it holds.

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

The success rate is quite good! However, I noticed that for the word **'loved'** it required 7 steps, which means it failed the Wordle game (since you only get 6 attempts).

![Log of the word 'loved' failing the puzzle](image-1.png)

But for most words, the bot does really well:

![Log of the bot solving for 'conch'](image-3.png)
![Log of the bot solving for 'honda'](image-2.png)

We can also solve for the word manually:

![Log of bot solving wordle manually for the word 'spool](image-4.png)

---

## Possible Solution Ideas

A possible solution is to take into account the frequency of usage of words in day-to-day life (using sources like Wikipedia). Since Wordle primarily uses rather common words as the solution, weighting common words higher might prevent the bot from guessing obscure words when a common one is available.

---

## What's Next?

I'm not sure what is next right now—maybe work on it a bit more to plot histograms of the guessed words, apply the frequency solution mentioned above, or make a "manual mode" to help me cheat at Wordle. I might also separate some scripts or port it to C or C++ as a learning experience.