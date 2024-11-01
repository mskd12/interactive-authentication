----------------------------------------------------------------

**This is an academic research prototype meant to elucidate concepts. It has not been developed in a production environment and is not meant for deployment.**

----------------------------------------------------------------

# Interactive Authentication

In this repository, you will find the associated code for the CCS'24 work on interactive authentication ([technical report](https://eprint.iacr.org/2022/1682)). 

1. Solidity smart contracts for the priority mechanism can be found in the contracts directory.

2. The main directory contains Python code to play around with different scenarios and the success probabilities of mechanisms. More details on this below:

    1. Given a priority or a majority mechanism, output its profile (DONE: See `maximal_mechanisms.py`)

    2. Write a function that returns the complete maximal set for 3-credential mechanisms (DONE: See `get_complete_maximal_set()` in `three_credentials.py`)

    3. Given a probability distribution, output the best mechanism from the complete maximal set. We can do this for 3-credential mechanisms. (DONE: See `best_mechanism.py`)

Interesting or useful extensions:

- A web app that implements task #3.

- Analyze which 3-cred maximal set mechanism is good in which settings? E.g., when should you use priority vs majority? Intuition says that majority is better with symmetric credentials (similar failure probs between creds) whereas priority is better with asymmetric ones, but can we arrive at it formally?

- Extend above tool for n>3. While we do not know the complete maximal sets, we can at least build a tool that outputs the best mechanism among the known maximal mechanisms. (This should not be too hard..)
