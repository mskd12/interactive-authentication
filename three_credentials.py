
from maximal_mechanisms import *
from utils import generate_all_binary_tuples

def get_all_majority_mechanisms() -> list[Mechanism]:
    """
    Generates all majority profiles using a tie-breaking mechanism.
    Doesn't exclude duplicates.

    Returns:
        list of tuples: A list where each tuple contains a label (str) and a profile (object).
    """
    all_tie_breaks = generate_all_binary_tuples(6)
    return [MajorityMechanism(3, lambda x, y: tie_breaker_function_3creds(x, y, tb), tb) for tb in all_tie_breaks]

def get_all_priority_mechanisms() -> list[Mechanism]:
    """
    Generate all priority profiles based on all possible rules and exceptions.
    Doesn't exclude duplicates.

    Returns:
        list of tuple: A list of tuples where each tuple contains a label (str) 
        describing the rule and exception, and the corresponding profile object.
    """
    mechanisms = []
    for rule in [[0, 1, 2], [1, 0, 2], [2, 0, 1], [0, 2, 1], [1, 2, 0], [2, 1, 0]]:
        for exception in [True, False]:
            m = PriorityMechanism(rule, exception)
            mechanisms.append(m)
    return mechanisms

def get_all_3cred_mechanisms():
    return get_all_majority_mechanisms() + get_all_priority_mechanisms()

def get_complete_maximal_set() -> list[Mechanism]:
    mechanisms = get_all_3cred_mechanisms()
    unique_mechanisms = []
    for m in mechanisms:
        if m not in unique_mechanisms:
            unique_mechanisms.append(m)
    return unique_mechanisms

def find_best_mechanisms(probabilities: list[CredentialProbabilities]):
    """
    Identifies the best mechanisms based on their success probabilities.

    This function evaluates a list of mechanisms and determines which ones have the highest 
    success probability given a list of credential probabilities. It iterates through each 
    mechanism, calculates the total success probability for each scenario in the mechanism's 
    profile, and compares it to find the best mechanisms.

    Args:
        probabilities (list[CredentialProbabilities]): A list of credential probabilities 
        used to calculate the success probability of each mechanism.

    Returns:
        tuple: A tuple containing the best mechanisms and their success probability
    """
    if len(probabilities) != 3:
        raise ValueError("Number of probabilities must match number of credentials")
    best_mechanisms = []
    best_profile_value = 0
    all_mechanisms = get_complete_maximal_set()
    for M in all_mechanisms:
        value = 0
        for scenario in M.profile:
            value += scenario.success_probability(probabilities)
        print(value, M)
        if value > best_profile_value:
            best_profile_value = value
            best_mechanisms = [M]
        elif value == best_profile_value:
            best_mechanisms.append(M)
    return (best_mechanisms, best_profile_value)
