
from enum import Enum
class St(Enum):
    THEFT = 0
    LEAKED = 1
    LOST = 2
    SAFE = 3

# THEFT is the worst, SAFE is the best. LEAKED and LOST undefined. 
# False doesn't necessarily imply "not worse or equal".
def worse_or_equal(st1, st2): # self is worse or equal than other
    if st1 == St.THEFT or st2 == St.SAFE:
        return True
    return False

class Scenario():
    def __init__(self, n, arr):
        self.n = n
        self.credentials = arr
        self.safe = 0
        self.leaked = 0
        self.lost = 0
        self.theft = 0
        for i in self.credentials:
            if i == St.SAFE:
                self.safe = self.safe + 1
            if i == St.THEFT:
                self.theft = self.theft + 1
            if i == St.LEAKED:
                self.leaked = self.leaked + 1
            if i == St.LOST:
                self.lost = self.lost + 1

    def __repr__(self):
        return "Scenario: %s" % (self.credentials)
    
    def __eq__(self, other):
        return self.n == other.n and self.credentials == other.credentials
    
    def priority_rule(self, rule: [int]) -> bool:
        for x in rule:
            if self.credentials[x] == St.SAFE:
                return True # User wins
            elif self.credentials[x] == St.THEFT:
                return False # Attacker wins
        return False # Corner case (no safe, theft)
    
    # Exception is (rule[1]) < (rule[2])
    def priority_rule_with_exception(self, rule:[int]) -> bool:
        if self.credentials[rule[0]] == St.LOST:
            if self.credentials[rule[1]] == St.SAFE and self.credentials[rule[2]] == St.THEFT:
                return False
            if self.credentials[rule[1]] == St.THEFT and self.credentials[rule[2]] == St.SAFE:
                return True
        for x in rule:
            if self.credentials[x] == St.SAFE:
                return True # User wins
            elif self.credentials[x] == St.THEFT:
                return False # Attacker wins
        return False # Corner case (no safe, theft)

    def is_complement(self, other) -> bool:
        if self.n != other.n:
            return False
        for idx, cred in enumerate(self.credentials):
            if cred == St.SAFE and other.credentials[idx] != St.THEFT:
                return False
            if cred == St.THEFT and other.credentials[idx] != St.SAFE:
                return False
            if cred == St.LEAKED and other.credentials[idx] != St.LEAKED:
                return False
            if cred == St.LOST and other.credentials[idx] != St.LOST:
                return False
        return True

    # Returns true only if for all credentials are worse or equal. In all other cases, returns false.
    def worse_or_equal(self, other) -> bool:
        if self.n != other.n:
            return False
        for i in range(self.n):
            if not worse_or_equal(self.credentials[i], other.credentials[i]):
                return False
        return True

def complement(s: Scenario):
    scomp = []
    for cred in s.credentials:
        if cred == St.LEAKED:
            scomp.append(St.LEAKED)
        elif cred == St.LOST:
            scomp.append(St.LOST)
        elif cred == St.SAFE:
            scomp.append(St.THEFT)
        else:
            scomp.append(St.SAFE)
    return Scenario(s.n, scomp)

scenario1 = Scenario(2, [St.SAFE, St.LEAKED])

import copy
from copy import deepcopy
import itertools
def recurse(n):
    if n == 1:
        return [Scenario(1, [St.THEFT]), 
                Scenario(1, [St.LEAKED]), 
                Scenario(1, [St.LOST]), 
                Scenario(1, [St.SAFE])]

    ret = recurse(n-1)
    # print(n, ret)
    final = []
    for st in St:
        for s in ret:
            creds1 = copy.deepcopy(s.credentials)
            creds1.append(st)
            final.append(Scenario(n, creds1))
    return final

num_creds = 3
all_scenarios = recurse(num_creds)

def is_special(s: Scenario):
    num_safe = 0
    num_theft = 0
    for cred in s.credentials:
        if cred == St.SAFE:
            num_safe = num_safe + 1
        elif cred == St.THEFT:
            num_theft = num_theft + 1
    return num_safe > 0 and num_theft > 0

special_scenarios = []

for s in all_scenarios:
    if is_special(s):
        special_scenarios.append(s)

print(len(all_scenarios))
print(len(special_scenarios))

# Step 1. List all optimal profiles
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

for v in itertools.product('01', repeat=len(rest)):
    profile = deepcopy(majority_profile_prefix)
    for i, scenario in enumerate(rest):
        if v[i] == '1':
            scenario = complement(scenario)
        profile.append(scenario)
    # print(profile)
    majority_profiles.append(profile)

print("#majority profiles:", len(majority_profiles))

priority_profiles = []

for rule in itertools.permutations([0, 1, 2]):
    profile1 = [] # normal
    profile2 = [] # exception
    for scenario in special_scenarios:
        if scenario.priority_rule(rule):
            profile1.append(deepcopy(scenario))
        if scenario.priority_rule_with_exception(rule):
            profile2.append(deepcopy(scenario))
    priority_profiles.append(profile1)
    priority_profiles.append(profile2)

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

from constraint import *

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
