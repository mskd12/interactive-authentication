from scenarios import Profile, St, CredentialProbabilities, generate_all_scenarios
from three_credentials import get_complete_maximal_set

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

# HDFC bank analysis below

def get_existing_profile():
    """The profile the current HDFC Bank mechanism"""
    all_scenarios = generate_all_scenarios(3)
    profile = []
    # Add all scenarios where mobile is safe
    for scenario in all_scenarios:
        if scenario.credential_states[1] == St.SAFE:
            profile.append(scenario)
        elif scenario.credential_states[1] == St.LOST and scenario.credential_states[2] == St.SAFE:
            profile.append(scenario)
    if len(profile) != 20:
        raise Exception("Error: Incorrect number of scenarios in profile")
    return Profile(profile)

# Sample credential probabilities to conduct our analysis...
# P(theft) = 0, P(leaked) = 0.15, P(lost) = 0.15, P(safe) = 0.7
password_state = CredentialProbabilities(0, 0.15, 0.15, 0.7)
# P(theft) = 0.1, P(leaked) = 0, P(lost) = 0, P(safe) = 0.9
otp_state = CredentialProbabilities(0.1, 0, 0, 0.9)
# P(theft) = 0, P(leaked) = 0, P(lost) = 0, P(safe) = 1
id_state = CredentialProbabilities(0, 0, 0, 1)
probabilities = [password_state, otp_state, id_state]

existing_profile = get_existing_profile()
existing_mechanism_success_prob = existing_profile.success_probability(probabilities)
print("Existing mechanism's success probability:", existing_mechanism_success_prob)

(suggested_best_mechanisms, new_success_prob) = find_best_mechanisms(probabilities)
print("New mechanism's success probability:", new_success_prob)
print("New mechanisms:", suggested_best_mechanisms)