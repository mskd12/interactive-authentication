from enum import Enum
class St(Enum):
    THEFT = 0
    LEAKED = 1
    LOST = 2
    SAFE = 3

# Note: This notion is only required for proving completeness of the 3-credential set.
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
    
    # TODO: Remove this function and instantiate a class for priority mechanisms
    # Returns true if the input priority mechanism (via the rule) succeeds in this scenario.
    def priority_rule(self, rule: [int]) -> bool:
        for x in rule:
            if self.credentials[x] == St.SAFE:
                return True # User wins
            elif self.credentials[x] == St.THEFT:
                return False # Attacker wins
        return False # Corner case (no safe, theft)
    
    # TODO: Remove this function and instantiate a class for PRE mechanisms
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


import copy
from copy import deepcopy
import itertools
def generate_all_scenarios(n):
    if n == 1:
        return [Scenario(1, [St.THEFT]), 
                Scenario(1, [St.LEAKED]), 
                Scenario(1, [St.LOST]), 
                Scenario(1, [St.SAFE])]

    ret = generate_all_scenarios(n-1)
    # print(n, ret)
    final = []
    for st in St:
        for s in ret:
            creds1 = copy.deepcopy(s.credentials)
            creds1.append(st)
            final.append(Scenario(n, creds1))
    return final

num_creds = 3
all_scenarios = generate_all_scenarios(num_creds)

# A scenario is special if it has at least one SAFE and one THEFT
def is_special(s: Scenario):
    num_safe = 0
    num_theft = 0
    for cred in s.credentials:
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

