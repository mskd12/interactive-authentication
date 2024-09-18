
from maximal_mechanisms import *
from utils import generate_all_binary_tuples

def get_all_majority_profiles():
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
