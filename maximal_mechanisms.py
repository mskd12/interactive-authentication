import itertools
import math
from typing import Callable, List
from scenarios import Scenario, St, generate_all_scenarios
from utils import compositions, generate_all_binary_tuples

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

class HierarchicalMechanism(Mechanism):
    # A hierarchical mechanism is defined by a rule and a tie breaker
    # The rule is a list of lists, each sublist contains the indices of credentials in a level
    #   the levels are ordered from the highest to the lowest.
    #   (Essentially, the rule defines a hierarchy of credentials)
    # The tie breaker is a function that takes two lists of indices and returns a boolean
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

    # Generate all the unique hierarchies for a given number of credentials
    #   |hierarchies| = |compositions(n)|
    @staticmethod
    def generate_all_hierarchies(n):
        all_possible_level_counts = compositions(n)
        hierarchies = []
        for counts in all_possible_level_counts:
            hierarchy = []
            cur_credential = 0
            for count in counts:
                hierarchy.append(list(range(cur_credential, cur_credential + count)))
                cur_credential += count
            hierarchies.append(hierarchy)
        return hierarchies
    
    # q(L) = \Pi^m_{i=1} (\binom{2l_i}{l_i} - 2^{n}) / 2
    @staticmethod
    def number_of_tie_breaks(counts):
        # check no empty levels
        if 0 in counts:
            raise Exception("Empty levels are not allowed")
        num_creds = sum(counts)
        result = 1
        for count in counts:
            result *= math.comb(2 * count, count)
        if result % 2 != 0:
            raise Exception("Result is not a power of 2")
        return (result - 2**(num_creds)) // 2
    
    @staticmethod
    def number_of_hierarchical_mechanisms(n):
        hierarchies = HierarchicalMechanism.generate_all_hierarchies(n)
        total = 0
        for hierarchy in hierarchies:
            counts = [len(level) for level in hierarchy]
            total += 2**(HierarchicalMechanism.number_of_tie_breaks(counts))
        return total

    # Doesn't bother to omit the isomorphisms and even some blatant duplicates
    # TODO: Remove the isomorphisms?
    @staticmethod
    def get_all_profiles(num_creds):
        num_levels = num_creds
        profiles = []
        rules = HierarchicalMechanism.generate_all_hierarchies(num_levels)
        print("Generated %s hierarchical rules with %d creds" % (rules, num_creds))
        for rule in rules:
            print("New rule: %s" % rule)
            ties = all_ties_to_break(rule)
            tie_breaker_options = generate_all_binary_tuples(len(ties))
            count = 0
            print("Rule %s has %d tie breakers" % (rule, len(tie_breaker_options)))
            for tb in tie_breaker_options:
                count += 1
                # Output a progress message every 10% of the way
                if len(tie_breaker_options) > 100 and count % (len(tie_breaker_options) // 10) == 0:
                    print("Progress: %d/%d" % (count, len(tie_breaker_options)))
                m = HierarchicalMechanism(num_creds, rule, lambda x, y: break_ties(x, y, ties, tb))
                p = m.profile()
                label = "hierarchical with rule %s and tie breaker %s" % (rule, tb)
                profiles.append((label, p))
        # print("Generated %d hierarchical profiles with %d creds" % (len(profiles), num_creds))
        # print(profiles)
        return profiles

#### We now provide some tools related to tie-breaking functions

def tie_break_inputs_for_hm(credentials):
    all_possible_inputs = []
    # Iterate over the length of the submitted set
    for length in range(len(credentials) + 1):
        # Generate all possible subsets of the submitted set of the given length
        S = list(itertools.combinations(credentials, length))
        for x in list(itertools.product(S, S)):
            all_possible_inputs.append(x)
    return all_possible_inputs

def all_ties_to_break(rule):
    all_possible_inputs_by_level = []
    for credentials in rule:
        x = tie_break_inputs_for_hm(credentials)
        # print(x)
        all_possible_inputs_by_level.append(x)
    y = itertools.product(*all_possible_inputs_by_level)
    all_possible_inputs = [(
                list(itertools.chain.from_iterable([elem[0] for elem in combination])),  # Merge first elements
                list(itertools.chain.from_iterable([elem[1] for elem in combination]))   # Merge second elements
            ) for combination in y]
    
    # remove elements where both tuples are the same
    all_possible_inputs = [x for x in all_possible_inputs if x[0] != x[1]]

    # remove inverse elements
    final_set = []
    for x in all_possible_inputs:
        if x not in final_set and (x[1], x[0]) not in final_set:
            final_set.append(x)
    
    return final_set

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
    raise Exception("Input not found (%s, %s) in %s" % (S1, S2, all_possible_inputs))

def tie_breaker_function_3creds(S1, S2, tie_breaker) -> bool:
    all_possible_inputs = generate_tie_break_inputs([0, 1, 2])
    # all_possible_one_inputs = [([0], [1]), ([0], [2]), ([1], [2])] # Omitting ([1], [0]), ([2], [0]), ([2], [1])
    # all_possible_two_inputs = [([0, 1], [1, 2]), ([0, 1], [0, 2]), ([1, 2], [0, 2])] # Omitting symmetric cases
    # all_possible_inputs = all_possible_one_inputs + all_possible_two_inputs
    return break_ties(S1, S2, all_possible_inputs, tie_breaker)

# Given a list of credential indices, generate all possible tie breaker inputs using these credentials
#   Omits the symmetric cases
def generate_tie_break_inputs(credential_list: List[int]):
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


# Note: Some clever method to generate all the majority profiles without computing the mechanism..?
# import itertools
# from copy import deepcopy

# for v in itertools.product('01', repeat=len(rest)):
#     profile = deepcopy(majority_profile_prefix)
#     for i, scenario in enumerate(rest):
#         if v[i] == '1':
#             scenario = complement(scenario)
#         profile.append(scenario)
#     # print(profile)
#     majority_profiles.append(profile)