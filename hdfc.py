# HDFC bank analysis below

from scenarios import CredentialProbabilities, Profile, generate_all_scenarios
from three_credentials import find_best_mechanisms


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