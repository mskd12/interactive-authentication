from copy import deepcopy
from typing import Callable, List
from scenarios import Scenario, St, generate_all_scenarios

# define an abstract base class for mechanisms
class Mechanism:
    def __init__(self, num_credentials):
        self.num_credentials = num_credentials
        pass

    def __repr__(self):
        pass

    def succeeds(self, scenario) -> bool:
        pass

    def profile(self) -> List[Scenario]:
        all_scenarios = generate_all_scenarios(self.num_credentials)
        return [scenario for scenario in all_scenarios if self.succeeds(scenario)]

# Models both priority and priority with exception mechanisms
class PriorityMechanism(Mechanism):
    # A priority mechanism is defined by a rule and whether an exception applies
    def __init__(self, rule: List[int], exception: bool):
        super().__init__(len(rule))
        self.rule = rule
        self.exception = exception
        if self.is_rule_well_defined() == False:
            raise Exception("Rule (%s) is not well defined" % (rule,))
    
    def is_rule_well_defined(self):
        # Sort it
        rule = sorted(self.rule)
        # Check if it is of the form [0, 1, 2, ... len(rule) - 1]
        for i in range(len(rule)):
            if rule[i] != i:
                return False
        return True
    
    def __repr__(self):
        if self.exception:
            return "PriorityMechanism: %s, exception" % (self.rule,)
        else:
            return "PriorityMechanism: %s, no exception" % (self.rule,)
    
    def succeeds(self, scenario):
        if self.exception:
            return self.priority_with_exception_judging_function(scenario)
        else:
            return self.priority_judging_function(scenario)

    def priority_judging_function(self, scenario) -> bool:
        rule = self.rule
        credentials = scenario.credential_states
        for x in rule:
            if credentials[x] == St.SAFE:
                return True # User wins
            elif credentials[x] == St.THEFT:
                return False # Attacker wins
        return False # Corner case (no safe, theft)

    def priority_with_exception_judging_function(self, scenario):
        rule = self.rule
        credentials = scenario.credential_states
        # Check if we are in the exception case
        # Since we assume all credentials are submitted by the parties, 
        #  exception occurs only if all but last two credentials are lost.
        if all([credentials[rule[i]] == St.LOST for i in range(len(rule) - 2)]):
            if credentials[rule[-2]] == St.SAFE and credentials[rule[-1]] == St.THEFT:
                return False
            if credentials[rule[-2]] == St.THEFT and credentials[rule[-1]] == St.SAFE:
                return True
        # Otherwise, apply the priority rule normally
        return self.priority_judging_function(scenario)


class MajorityMechanism(Mechanism):
    def __init__(self, num_credentials, 
                 tie_breaker: Callable[[List[int], List[int]], bool]):
        super().__init__(num_credentials)
        self.tie_breaker = tie_breaker
    
    def __repr__(self):
        return """MajorityMechanism with %s credentials and 
                tie breaker %s""" % (self.num_credentials, self.tie_breaker,)
    
    def succeeds(self, scenario):
        # Count the number of credentials known to the user and the attacker
        user_credentials = [i for (i, cred) in enumerate(scenario.credential_states) 
                            if cred == St.SAFE or cred == St.LEAKED]
        attacker_credentials = [i for (i, cred) in enumerate(scenario.credential_states) 
                                if cred == St.THEFT or cred == St.LEAKED]

        user_count = len(user_credentials)
        attacker_count = len(attacker_credentials)

        if user_count > attacker_count:
            return True
        elif user_count < attacker_count:
            return False
        elif user_credentials == attacker_credentials: # Both submit same credentials!
            return False
        else:
            return self.tie_breaker(user_credentials, attacker_credentials)

class HierarchicalMechanism(Mechanism):
    def __init__(self, num_credentials, 
                 rule: List[List[int]], 
                 tie_breaker: Callable[[List[int], List[int]], bool]):
        super().__init__(num_credentials)
        self.rule = rule
        self.tie_breaker = tie_breaker
        if self.is_rule_well_defined() == False:
            raise Exception("Rule (%s) is not well defined" % (rule,))
    
    def __repr__(self):
        return """HierarchicalMechanism with %s credentials and 
                priority rule %s and tie breaker %s""" % (self.num_credentials, self.rule, self.tie_breaker,)
    
    def is_rule_well_defined(self):
        # Merge and sort it
        rule = sorted([x for sublist in self.rule for x in sublist])
        # Check if it is of the form [0, 1, 2, ... len(rule) - 1]
        for i in range(len(rule)):
            if rule[i] != i:
                return False
        return True

    def succeeds(self, scenario) -> bool:
        user_credentials = [i for (i, cred) in enumerate(scenario.credential_states) 
                            if cred == St.SAFE or cred == St.LEAKED]
        attacker_credentials = [i for (i, cred) in enumerate(scenario.credential_states) 
                                if cred == St.THEFT or cred == St.LEAKED]

        # Go level by level, starting from the highest level
        for i in range(len(self.rule)):
            user_credentials_level = len([x for x in user_credentials if x in self.rule[i]])
            attacker_credentials_level = len([x for x in attacker_credentials if x in self.rule[i]])
            if user_credentials_level > attacker_credentials_level:
                return True
            elif user_credentials_level < attacker_credentials_level:
                return False

        # If we reach here, we need to apply the tie breaker
        if user_credentials == attacker_credentials:
            return False
        return self.tie_breaker(user_credentials, attacker_credentials)

#### We now provide some tools related to tie-breaking functions

# n = 6 for generating tie-breaks for 3 credentials
# Generate all possible n-tuples, e.g., if n=6, (0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1), ...
def enumerate_all_tie_breaking_functions(n):
    all_tie_breakers = []
    for i in range(2**n):
        tie_breaker = []
        for j in range(n):
            tie_breaker.append((i >> j) & 1)
        all_tie_breakers.append(tie_breaker)
    return all_tie_breakers

# S1 is submitted by the user, S2 is submitted by the attacker
# all_possible_inputs is a list of tuples, each tuple is a pair of sets
#   these correspond to the all possible (S1, S2)'s
# tie_breaker is a list of 0s and 1s, each 0 or 1 corresponds to the evaluation of the corresponding input
def break_ties(S1, S2, all_possible_inputs, tie_breaker) -> bool:
    if len(all_possible_inputs) != len(tie_breaker):
        raise Exception("Input size does not match tie breaker size %s %s" % (all_possible_inputs, tie_breaker))

    combined = zip(all_possible_inputs, tie_breaker)
    for (an_input, evaluation) in list(combined):
        if an_input == (S1, S2):
            return bool(evaluation)
        elif an_input == (S2, S1):
            return bool(1 - evaluation)
    raise Exception("Input not found %s %s" % (S1, S2))

def tie_breaker_function_3creds(S1, S2, tie_breaker) -> bool:
    all_possible_one_inputs = [([0], [1]), ([0], [2]), ([1], [2])] # Omitting ([1], [0]), ([2], [0]), ([2], [1])
    all_possible_two_inputs = [([0, 1], [1, 2]), ([0, 1], [0, 2]), ([1, 2], [0, 2])] # Omitting symmetric cases
    all_possible_inputs = all_possible_one_inputs + all_possible_two_inputs
    return break_ties(S1, S2, all_possible_inputs, tie_breaker)

## We now define some specific tie breaking functions (these are included in the above functions)

# Uniform priority tie breaker: applies the priority rule uniformly
def uniform_priority_tie_breaker(S1: List[int], S2: List[int], rule: List[int]) -> bool:
    if len(S1) != len(S2):
        raise Exception("S1 and S2 must have the same length")
    for x in rule:
        if x in S1 and x not in S2:
            return True
        if x in S2 and x not in S1:
            return False
    return False

# Different priority rule for sets of different lengths
# rule[i-1] defines priority rule for sets of length i
def different_priority_tie_breaker(S1: List[int], S2: List[int], rule: List[List[int]]) -> bool:
    if len(S1) != len(S2):
        raise Exception("S1 and S2 must have the same length %s %s" % (S1, S2))
    if len(S1) > len(rule):
        raise Exception("Rule %s is not defined for sets of length %s" % (rule, len(S1)))
    selected_rule = rule[len(S1) - 1]
    for x in selected_rule:
        if x in S1 and x not in S2:
            return True
        if x in S2 and x not in S1:
            return False
    return False
