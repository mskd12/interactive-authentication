# Constrains the set of all possible profiles to find a profile that is incomparable to all optimal profiles.
# This serves as a proof that the set of all known 3-credential profiles is complete.
# Refer to the paper for more details. In broad strokes, we do:
# Step 1. List all optimal profiles (among the special scenarios only)
# Step 2. Try to find a profile incomparable to all and satisfying some constraints

import itertools
from scenarios import can_coexist_in_profile, complement, Scenario, generate_all_scenarios, is_special
from three_credentials import get_all_majority_profiles, get_all_priority_profiles

num_creds = 3
all_scenarios = generate_all_scenarios(num_creds)
special_scenarios = [s for s in all_scenarios if is_special(s)]
special_scenarios_without_complements = []
for s in special_scenarios:
    if complement(s) not in special_scenarios_without_complements:
        special_scenarios_without_complements.append(s)
complements = [complement(s) for s in special_scenarios_without_complements]

print("#special scenarios:", len(special_scenarios))
print("#special scenarios without complements:", len(special_scenarios_without_complements))

optimal_profiles = []

majority_profiles = []
majority_profiles_raw = get_all_majority_profiles()
for (_, profile) in majority_profiles_raw:
    special_scenarios_only = [s for s in profile if is_special(s)]
    majority_profiles.append(special_scenarios_only)

print("#majority profiles:", len(majority_profiles))

priority_profiles = []
priority_profiles_raw = get_all_priority_profiles()
for (_, profile) in priority_profiles_raw:
    special_scenarios_only = [s for s in profile if is_special(s)]
    priority_profiles.append(special_scenarios_only)

print("#priority profiles:", len(priority_profiles))

for p in majority_profiles:
    optimal_profiles.append(p)

for p in priority_profiles:
    optimal_profiles.append(p)

# Test
for idx1, profile1 in enumerate(optimal_profiles):
    for idx2, profile2 in enumerate(optimal_profiles):
        if idx1 != idx2 and profile1 == profile2:
            print("Terror")

# not really all possible profiles.. more like all possible special scenarios in prof(M), denoted by S
all_possible_profiles = []

# Checks if the profile contains scenarios s1 and s2 s.t. complement(s2) is worse than s1.
def is_valid_profile(profile: [Scenario]) -> bool:
    for s in profile:
        for s1 in profile:
            if not can_coexist_in_profile(s, s1):
                return False
    return True

for v in itertools.product([0, 1], repeat=len(special_scenarios_without_complements)):
    profile = []
    for idx, x in enumerate(v):
        s = None
        if x == 0:
            s = special_scenarios_without_complements[idx]
        elif x == 1:
            s = complements[idx]
        profile.append(s)
    if len(profile) == 0:
        continue
    all_possible_profiles.append(profile)

# assert len(all_possible_profiles) == 3**len(half_special_scenarios) - 1
print("#all possible profiles:", len(all_possible_profiles))

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

# P(M) must contain at least one of the complements of the special scenarios in order to be incomparable.
# The implementation is doing a complement of all scenarios, which is not required, but not wrong either.
def no_clashes(profile: [Scenario]) -> bool:
    for opt in optimal_profiles:
        c = []
        # print(opt)
        for s in opt:
            c.append(complement(s))
        # print(c)
        if len(intersection(c, profile)) == 0:
            return False
    return True

from constraint import Problem

def constraintSolve():
    problem = Problem()
    problem.addVariable("s", all_possible_profiles)
    # problem.addConstraint(no_clashes, "s")
    problem.addConstraint(is_valid_profile, "s")
    solutions = problem.getSolutions()
    print(len(solutions))
    if len(solutions) > 0:
        print(solutions[0])

if __name__ == '__main__':
    constraintSolve()
