"""
This module defines a set of classes and functions to handle scenarios involving different credential states.
It includes:
- An enumeration `St` representing different states of credentials (THEFT, LEAKED, LOST, SAFE).
- A `Scenario` class to represent a scenario with multiple credentials and methods to compare and manipulate them.
- Functions to generate all possible scenarios and special scenarios.
- Utility functions to check if scenarios can coexist in a profile and to determine if a scenario is special.
"""

from enum import Enum
from itertools import permutations
class St(Enum):
    THEFT = 0
    LEAKED = 1
    LOST = 2
    SAFE = 3

class CredentialProbabilities:
    def __init__(self, theft_prob: float, leaked_prob: float, lost_prob: float, safe_prob: float):
        total_prob = theft_prob + leaked_prob + lost_prob + safe_prob
        if not (0 <= theft_prob <= 1 and 0 <= leaked_prob <= 1 and 0 <= lost_prob <= 1 and 0 <= safe_prob <= 1):
            raise ValueError("Probabilities must be between 0 and 1.")
        if total_prob != 1:
            raise ValueError("Probabilities must sum to 1.")
        self.theft_prob = theft_prob
        self.leaked_prob = leaked_prob
        self.lost_prob = lost_prob
        self.safe_prob = safe_prob

    def __repr__(self):
        return (f"CredentialProbabilities(THEFT={self.theft_prob}, "
                f"LEAKED={self.leaked_prob}, LOST={self.lost_prob}, SAFE={self.safe_prob})")
    
    def get_probability(self, state: St) -> float:
        if state == St.THEFT:
            return self.theft_prob
        if state == St.LEAKED:
            return self.leaked_prob
        if state == St.LOST:
            return self.lost_prob
        if state == St.SAFE:
            return self.safe_prob
        raise ValueError("Invalid state")

# Note: This notion is only required for proving completeness of the 3-credential set.
# False doesn't necessarily imply "not worse or equal".
# st2 & st1
# \stSafe &\mapsto \stSafe / \stLeaked / \stLost / \stStolen \\
# \stStolen &\mapsto \stStolen \\
# \stLeaked &\mapsto \stLeaked / \stStolen \\
# \stLost &\mapsto \stLost / \stStolen.
def worse_or_equal(st1, st2): # self is worse or equal than other
    if st1 == St.THEFT or st2 == St.SAFE or st1 == st2:
        return True
    return False

class Scenario():
    def __init__(self, arr):
        self.credential_states = arr
        self.n = len(arr)
        self.safe = 0
        self.leaked = 0
        self.lost = 0
        self.theft = 0
        for i in self.credential_states:
            if i == St.SAFE:
                self.safe = self.safe + 1
            if i == St.THEFT:
                self.theft = self.theft + 1
            if i == St.LEAKED:
                self.leaked = self.leaked + 1
            if i == St.LOST:
                self.lost = self.lost + 1

    def __repr__(self):
        return "Scenario: %s" % (self.credential_states)
    
    def __eq__(self, other):
        return self.n == other.n and self.credential_states == other.credential_states
    
    def __hash__(self):
        return hash(tuple(self.credential_states))
    
    def is_complement(self, other) -> bool:
        if self.n != other.n:
            return False
        for idx, cred in enumerate(self.credential_states):
            if cred == St.SAFE and other.credential_states[idx] != St.THEFT:
                return False
            if cred == St.THEFT and other.credential_states[idx] != St.SAFE:
                return False
            if cred == St.LEAKED and other.credential_states[idx] != St.LEAKED:
                return False
            if cred == St.LOST and other.credential_states[idx] != St.LOST:
                return False
        return True

    # Returns true only if for all credentials are worse or equal. 
    #  In all other cases, returns false.
    def worse_or_equal(self, other) -> bool:
        if self.n != other.n:
            return False
        for i in range(self.n):
            if not worse_or_equal(self.credential_states[i], other.credential_states[i]):
                return False
        return True

    def success_probability(self, probabilities: list[CredentialProbabilities]) -> float:
        if len(probabilities) != self.n:
            raise ValueError("Number of probabilities must match number of credentials")
        probability = 1
        for i, state in enumerate(self.credential_states):
            probability *= probabilities[i].get_probability(state)
        return probability

class Profile:
    def __init__(self, scenarios: list[Scenario]):
        self.scenarios = scenarios

    def __len__(self):
        return len(self.scenarios)

    def __getitem__(self, index):
        return self.scenarios[index]

    def __setitem__(self, index, value):
        self.scenarios[index] = value

    def __delitem__(self, index):
        del self.scenarios[index]

    def __iter__(self):
        return iter(self.scenarios)

    def __contains__(self, item):
        return item in self.scenarios

    def __repr__(self):
        return f"Profile({self.scenarios})"
    
    def __eq__(self, other):
        if not isinstance(other, Profile):
            return NotImplemented
        if len(self) != len(other):
            return False
        n = len(self.scenarios[0].credential_states) # Number of credentials
        # Look at all the credential permutations
        for perm in permutations(range(n)):
            # Permute self
            permuted_self = set()
            for s in self.scenarios:
                new_states = [s.credential_states[i] for i in perm]
                permuted_self.add(Scenario(new_states))
            # Check if other is same as permuted self
            if set(other) == permuted_self:
                return True
        return False
    
    def success_probability(self, probabilities: list[CredentialProbabilities]) -> float:
        value = 0
        for scenario in self.scenarios:
            value += scenario.success_probability(probabilities)
        return value


def complement(s: Scenario):
    scomp = []
    for cred in s.credential_states:
        if cred == St.LEAKED:
            scomp.append(St.LEAKED)
        elif cred == St.LOST:
            scomp.append(St.LOST)
        elif cred == St.SAFE:
            scomp.append(St.THEFT)
        else:
            scomp.append(St.SAFE)
    return Scenario(scomp)

from copy import deepcopy
def generate_all_scenarios_internal(n):
    if n == 1:
        return [Scenario([St.THEFT]), 
                Scenario([St.LEAKED]), 
                Scenario([St.LOST]), 
                Scenario([St.SAFE])]

    ret = generate_all_scenarios_internal(n-1)
    final = []
    for st in St:
        for s in ret:
            creds1 = deepcopy(s.credential_states)
            creds1.append(st)
            final.append(Scenario(creds1))
    return final

ALL_SCENARIOS = [generate_all_scenarios_internal(i) for i in range(1, 10)]

# Cache the scenarios
def generate_all_scenarios(n):
    MAX_SUPPORTED = len(ALL_SCENARIOS)
    if n > MAX_SUPPORTED:
        raise Exception(n, "is not supported. Max supported is", MAX_SUPPORTED)
    return ALL_SCENARIOS[n - 1]

# A scenario is special if it has at least one SAFE and one THEFT credential.
def is_special(s: Scenario):
    num_safe = 0
    num_theft = 0
    for cred in s.credential_states:
        if cred == St.SAFE:
            num_safe = num_safe + 1
        elif cred == St.THEFT:
            num_theft = num_theft + 1
    return num_safe > 0 and num_theft > 0

def generate_all_special_scenarios(n):
    all_scenarios = generate_all_scenarios(n)
    special_scenarios = []
    for s in all_scenarios:
        if is_special(s):
            special_scenarios.append(s)
    return special_scenarios

# Can s1 and s2 be in the same profile?
# They can't if the complement of one (won by the attacker) is worse or equal to the other (won by the user).
def can_coexist_in_profile(s1: Scenario, s2: Scenario) -> bool:
    if complement(s2).worse_or_equal(s1) or complement(s1).worse_or_equal(s2):
        return False
    return True

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
