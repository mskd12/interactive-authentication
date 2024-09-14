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
        self.credential_states = arr
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
    return Scenario(s.n, scomp)


from copy import deepcopy
def generate_all_scenarios_internal(n):
    if n == 1:
        return [Scenario(1, [St.THEFT]), 
                Scenario(1, [St.LEAKED]), 
                Scenario(1, [St.LOST]), 
                Scenario(1, [St.SAFE])]

    ret = generate_all_scenarios_internal(n-1)
    final = []
    for st in St:
        for s in ret:
            creds1 = deepcopy(s.credential_states)
            creds1.append(st)
            final.append(Scenario(n, creds1))
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
