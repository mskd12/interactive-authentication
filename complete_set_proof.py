from copy import deepcopy
import itertools
from scenarios import St, complement, Scenario, generate_all_scenarios
from three_credentials import get_all_majority_profiles, get_all_priority_profiles

# THEFT is the worst, SAFE is the best. LEAKED and LOST undefined. 
# False doesn't necessarily imply "not worse or equal".
def worse_or_equal(st1, st2): # self is worse or equal than other
    if st1 == St.THEFT or st2 == St.SAFE:
        return True
    return False

num_creds = 3
all_scenarios = generate_all_scenarios(num_creds)

# Special scenario: contains at least one safe and one theft credential
def is_special(s: Scenario):
    num_safe = 0
    num_theft = 0
    for cred in s.credential_states:
        if cred == St.SAFE:
            num_safe = num_safe + 1
        elif cred == St.THEFT:
            num_theft = num_theft + 1
    return num_safe > 0 and num_theft > 0

special_scenarios = []

for s in all_scenarios:
    if is_special(s):
        special_scenarios.append(s)

print("#special scenarios:", len(special_scenarios))

# Step 1. List all optimal profiles (among the special scenarios only)
# Step 2. Try to find a profile incomparable to all and satisfying some constraints

optimal_profiles = []

majority_profile_prefix = [Scenario(3, [St.SAFE, St.SAFE, St.THEFT]), 
                           Scenario(3, [St.SAFE, St.THEFT, St.SAFE]),
                           Scenario(3, [St.THEFT, St.SAFE, St.SAFE])]

rest = [Scenario(3, [St.SAFE, St.LEAKED, St.THEFT]), 
        Scenario(3, [St.LEAKED, St.THEFT, St.SAFE]),
        Scenario(3, [St.THEFT, St.SAFE, St.LEAKED]),
        Scenario(3, [St.SAFE, St.LOST, St.THEFT]), 
        Scenario(3, [St.LOST, St.THEFT, St.SAFE]),
        Scenario(3, [St.THEFT, St.SAFE, St.LOST])]

# Test
for x in majority_profile_prefix:
    if not (x in special_scenarios):
        print("Terror")
for x in rest:
    if not (x in special_scenarios):
        print("Terror")

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
    assert(len(p)) == len(special_scenarios) / 2
    optimal_profiles.append(p)

for p in priority_profiles:
    assert(len(p)) == len(special_scenarios) / 2
    optimal_profiles.append(p)

# Test
for idx1, profile1 in enumerate(optimal_profiles):
    for idx2, profile2 in enumerate(optimal_profiles):
        if idx1 != idx2 and profile1 == profile2:
            print("Terror")

# not really all possible profiles.. more like all possible special scenarios in prof(M), denoted by S
all_possible_profiles = []

half_special_scenarios = []
complements = []
for s in majority_profile_prefix:
    half_special_scenarios.append(deepcopy(s))
    complements.append(complement(s))
for s in rest:
    half_special_scenarios.append(deepcopy(s))
    complements.append(complement(s))

assert len(half_special_scenarios) == len(special_scenarios) / 2

for v in itertools.product([0, 1, 2], repeat=len(half_special_scenarios)):
    profile = []
    for idx, x in enumerate(v):
        if x == 1:
            profile.append(half_special_scenarios[idx])
        elif x == 2:
            profile.append(complements[idx])
    if len(profile) == 0:
        continue
    all_possible_profiles.append(profile)

assert len(all_possible_profiles) == 3**(len(special_scenarios) / 2) - 1

# print(all_possible_profiles[0], all_possible_profiles[-1])

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

# Checks if the profile contains scenarios s1 and s2 s.t. complement(s2) is worse than s1.
def is_valid_profile(profile: [Scenario]) -> bool:
    for s in profile:
        c = complement(s) # c is won by the attacker (because it is a complement)
        for s1 in profile: # finding a scenario that is worse than c and won by the user
            if s1.worse_or_equal(c):
                return False
    return True

from constraint import Problem

def constraintSolve():
    problem = Problem()
    problem.addVariable("s", all_possible_profiles)
    problem.addConstraint(no_clashes, "s")
    problem.addConstraint(is_valid_profile, "s")
    solutions = problem.getSolutions()
    print(len(solutions))
    if len(solutions) > 0:
        print(solutions[0])

if __name__ == '__main__':
    constraintSolve()
