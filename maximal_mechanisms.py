"""
This module defines abstract base classes and specific implementations for priority and majority mechanisms.
"""

import itertools
import math
from typing import Callable
from scenarios import CredentialProbabilities, Profile, St, generate_all_scenarios

# An abstract base class for mechanisms
class Mechanism:
    """
    A mechanism that determines the success of a scenario based on predefined rules.

    Attributes:
        num_credentials (int): The number of credentials involved in the mechanism.
        profile (Profile): The profile (scenarios where the mechanism succeeds).

    Methods:
        __repr__(): Returns a string representation of the Mechanism instance.
        succeeds(scenario): Determines if the mechanism succeeds for a given scenario.
    """
    def __init__(self, num_credentials):
        self.num_credentials = num_credentials
        self.profile = self.compute_profile()
        pass

    def succeeds(self, scenario) -> bool:
        pass

    def label(self) -> str:
        pass

    def __repr__(self):
        return self.label()

    def compute_profile(self) -> Profile:
        all_scenarios = generate_all_scenarios(self.num_credentials)
        return Profile([scenario for scenario in all_scenarios if self.succeeds(scenario)])

    def __eq__(self, other):
        return self.profile == other.profile
 
    def success_probability(self, probabilities: list[CredentialProbabilities]) -> float:
        return self.profile.success_probability(probabilities)

# Models both priority and priority with exception mechanisms
class PriorityMechanism(Mechanism):
    """
    A mechanism that determines the success of a user based on a priority rule and an optional exception.
    Attributes:
        rule (list[int]): A list of integers representing the priority rule.
        exception (bool): A boolean indicating whether an exception applies to the mechanism.
    Methods:
        __init__(rule, exception): Initializes the PriorityMechanism with a given rule and exception flag.
        is_rule_well_defined(): Checks if the rule is well-defined. A rule is well-defined if it is a permutation of [0, 1, 2, ..., len(rule) - 1].
        __repr__(): Returns a string representation of the PriorityMechanism, indicating the rule and whether an exception applies.
        succeeds(scenario): Determines if the mechanism succeeds given a scenario. Applies the appropriate judging function based on the exception flag.
        priority_judging_function(scenario): The default judging function based on the priority rule. Returns True if a user wins, False if an attacker wins.
        priority_with_exception_judging_function(scenario): The judging function that considers the exception case. Applies the priority rule normally if the exception does not occur.
    """
   # A priority mechanism is defined by a rule and whether an exception applies
    def __init__(self, rule: list[int], exception: bool):
        self.rule = rule
        self.exception = exception
        if self.is_rule_well_defined() == False:
            raise Exception("Rule (%s) is not well defined" % (rule,))
        super().__init__(len(rule))
    
    def is_rule_well_defined(self):
        # Sort it
        rule = sorted(self.rule)
        # Check if it is of the form [0, 1, 2, ... len(rule) - 1]
        for i in range(len(rule)):
            if rule[i] != i:
                return False
        return True
    
    def label(self):
        return "priority with rule %s and exception %s" % (self.rule, self.exception)
    
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
    """
    A mechanism that determines the success of a user based on the majority of credentials.
    Attributes:
        num_credentials (int): The number of credentials involved in the mechanism.
        tie_breaker_func (Callable[[list[int], list[int]], bool]): A function to resolve ties between user and attacker credentials.
        tie_break_label (list[int]): A list of binary evaluations corresponding to each pair of tie-breaking inputs. It is there solely for labelling purposes.
    Note: tie_break_label alone should in theory be enough to define a tie breaker. But I had some issues removing tie_breaker_func and solely depending on it.
    Methods:
        __repr__(): Returns a string representation of the MajorityMechanism instance.
        succeeds(scenario): Determines if the user succeeds based on the given scenario.
        number_of_tie_breaks(num_creds): Calculates the number of tie breaks for a given number of credentials.
        number_of_majority_mechanisms(n): Calculates the number of possible majority mechanisms for a given number of credentials.
    """
    def __init__(self, num_credentials, 
                 tie_breaker_func: Callable[[list[int], list[int]], bool],
                 tie_break_label: list[int]):
        self.tie_breaker_func = tie_breaker_func
        self.tie_break_label = tie_break_label
        super().__init__(num_credentials)
    
    def label(self):
        return """majority with %s creds and tie-breaker %s""" % (self.num_credentials, self.tie_break_label,)
    
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
            return self.tie_breaker_func(user_credentials, attacker_credentials)

    # (2n C n) - 2**n / 2
    @staticmethod
    def number_of_tie_breaks(num_creds):
        x = (math.comb(2 * num_creds, num_creds) - 2**num_creds)
        if x % 2 != 0:
            raise Exception("Result is not a power of 2")
        return x // 2
    
    @staticmethod
    def number_of_majority_mechanisms(n):
        return 2**(MajorityMechanism.number_of_tie_breaks(n))

#### We now provide some tools related to tie-breaking functions

def break_ties(S1, S2, all_possible_inputs, tie_breaker) -> bool:
    """
    Determines the outcome of a tie between two sets S1 and S2 based on a predefined tie breaker.

    Args:
        S1: The user-submitted set involved in the tie.
        S2: The attacker-submitted set involved in the tie.
        all_possible_inputs: A list of all possible input pairs that can be compared.
        tie_breaker: A list of binary evaluations corresponding to each pair in all_possible_inputs.

    Returns:
        bool: The result of the tie-breaking evaluation. Returns True or False based on the tie_breaker.

    Raises:
        Exception: If the length of all_possible_inputs does not match the length of tie_breaker.
        Exception: If the input pair (S1, S2) or (S2, S1) is not found in all_possible_inputs.
    """
    if len(all_possible_inputs) != len(tie_breaker):
        raise Exception("Input size does not match tie breaker size %s %s" % (all_possible_inputs, tie_breaker))

    combined = zip(all_possible_inputs, tie_breaker)
    for (an_input, evaluation) in list(combined):
        if an_input == (S1, S2):
            return bool(evaluation)
        elif an_input == (S2, S1):
            return bool(1 - evaluation)
    raise Exception("Input not found (%s, %s) in %s" % (S1, S2, all_possible_inputs))

def tie_breaker_function_3creds(S1, S2, tie_breaker) -> bool:
    """
    Determines the outcome of a tie-breaking mechanism for three credentials.

    This function generates all possible tie-breaking inputs for three credentials
    and uses a provided tie-breaking function to resolve ties between two sets of credentials.

    Args:
        S1 (list): The first set of credentials.
        S2 (list): The second set of credentials.
        tie_breaker (function): A function that resolves ties between two sets of credentials.

    Returns:
        bool: The result of the tie-breaking function applied to the given sets of credentials.
    """
    all_possible_inputs = generate_tie_break_inputs([0, 1, 2])
    # all_possible_one_inputs = [([0], [1]), ([0], [2]), ([1], [2])] # Omitting ([1], [0]), ([2], [0]), ([2], [1])
    # all_possible_two_inputs = [([0, 1], [1, 2]), ([0, 1], [0, 2]), ([1, 2], [0, 2])] # Omitting symmetric cases
    # all_possible_inputs = all_possible_one_inputs + all_possible_two_inputs
    return break_ties(S1, S2, all_possible_inputs, tie_breaker)

def generate_tie_break_inputs(credential_list: list[int]):
    """
    Generates all possible tie-breaking input pairs from a list of credentials.

    This function takes a list of credentials and generates all possible pairs of 
    subsets (S1, S2) such that S1 and S2 have the same length, S1 is not equal to S2, 
    and the pair (S2, S1) is not already included in the output list.

    Args:
        credential_list (list[int]): A list of credentials represented as integers.

    Returns:
        list[Tuple[list[int], list[int]]]: A list of tuples, where each tuple contains 
        two lists representing the tie-breaking input pairs.
    """
    all_possible_inputs = []
    for tie_length in range(len(credential_list)): # 1, 2, ..., len(credentials) - 1
        if tie_length == 0:
            continue
        for S1 in itertools.combinations(credential_list, tie_length):
            for S2 in itertools.combinations(credential_list, tie_length):
                if S1 != S2 and (list(S2), list(S1)) not in all_possible_inputs:
                    all_possible_inputs.append((list(S1), list(S2)))
    return all_possible_inputs

## We now define some specific tie breaking functions (these are included in the above functions)

# Uniform priority tie breaker: applies the priority rule uniformly
def uniform_priority_tie_breaker(S1: list[int], S2: list[int], rule: list[int]) -> bool:
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
def different_priority_tie_breaker(S1: list[int], S2: list[int], rule: list[list[int]]) -> bool:
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
