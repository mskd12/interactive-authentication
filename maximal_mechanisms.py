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
        if self.is_rule_well_defined(rule) == False:
            raise Exception("Rule (%s) is not well defined" % (rule,))
        self.rule = rule
        self.exception = exception
    
    def is_rule_well_defined(self, rule):
        # Sort it
        rule = sorted(rule)
        # Check if it is of the form [0, 1, 2, ... len(rule) - 1]
        for i in range(len(rule)):
            if rule[i] != i:
                return False
    
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

def enumerate_all_tie_breaking_functions_for_3_creds():
    all_tie_breakers = []
    # len(all_possible_inputs) in the tie_breaker_function is 6
    # So a tie-breaker can decide in 2^6 = 64 ways. 
    # Generate all possible 6-tuples (0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1), ...
    for i in range(2**6):
        tie_breaker = []
        for j in range(6):
            tie_breaker.append((i >> j) & 1)
        all_tie_breakers.append(tie_breaker)
    return all_tie_breakers

def tie_breaker_function_3creds(S1, S2, tie_breaker) -> bool:
    all_possible_one_inputs = [([0], [1]), ([0], [2]), ([1], [2])] # Omitting ([1], [0]), ([2], [0]), ([2], [1])
    all_possible_two_inputs = [([0, 1], [1, 2]), ([0, 1], [0, 2]), ([1, 2], [0, 2])] # Omitting symmetric cases
    all_possible_inputs = all_possible_one_inputs + all_possible_two_inputs

    combined = zip(all_possible_inputs, tie_breaker)
    for (an_input, evaluation) in list(combined):
        if an_input == (S1, S2):
            return bool(evaluation)
        elif an_input == (S2, S1):
            return bool(1 - evaluation)
    raise Exception("Input not found %s %s %s" % (S1, S2, list(combined)))

def uniform_priority_tie_breaker(S1: List[int], S2: List[int], rule: List[int]) -> bool:
    if len(S1) != len(S2):
        raise Exception("S1 and S2 must have the same length")
    for x in rule:
        if x in S1 and x not in S2:
            return True
        if x in S2 and x not in S1:
            return False
    return False

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
