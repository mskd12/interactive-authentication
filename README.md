# Interactive Authentication

1. Solidity smart contracts for the priority mechanism can be found in the smart-contracts directory.

2. The main directory contains Python code to play around with different scenarios and the success probabilities of mechanisms. More details on this below:

Goals:

- Given a priority or a majority mechanism, output its profile (DONE)

- Write a function that returns the complete maximal set for 3-credential mechanisms (Close; get_all_3cred_profiles returns all the 3-credential majority, priority mechanisms)

- Given a probability distribution, output the best mechanism from the complete maximal set. We can do this for 3-credential mechanisms. 

- Note: For n>3, we could build a tool that outputs the best mechanism among the known maximal mechanisms.
