
from maximal_mechanisms import *
from utils import generate_all_binary_tuples

def get_all_majority_profiles():
    """
    Generates all majority profiles using a tie-breaking mechanism.

    Returns:
        list of tuples: A list where each tuple contains a label (str) and a profile (object).
    """
    # First get all majority profiles
    all_tie_breaks = generate_all_binary_tuples(6)
    profiles = []
    for tb in all_tie_breaks:
        m = MajorityMechanism(3, lambda x, y: tie_breaker_function_3creds(x, y, tb))
        p = m.profile()
        label = "majority with %s" % (tb,)
        profiles.append((label, p))
    return profiles

def get_all_priority_profiles():
    """
    Generate all priority profiles based on all possible rules and exceptions.

    Returns:
        list of tuple: A list of tuples where each tuple contains a label (str) 
        describing the rule and exception, and the corresponding profile object.
    """
    profiles = []
    for rule in [[0, 1, 2], [1, 0, 2], [2, 0, 1], [0, 2, 1], [1, 2, 0], [2, 1, 0]]:
        for exception in [True, False]:
            m = PriorityMechanism(rule, exception)
            p = m.profile()
            label = "priority with rule %s and exception %s" % (rule, exception)
            profiles.append((label, p))
    return profiles

def get_all_3cred_profiles():
    return get_all_majority_profiles() + get_all_priority_profiles()
