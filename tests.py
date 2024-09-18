from scenarios import *
from maximal_mechanisms import *

import unittest

from three_credentials import *
from utils import generate_all_binary_tuples, remove_duplicates
import utils

class TestScenarios(unittest.TestCase):
    def test_all_scenarios(self):
        all_scenarios = generate_all_scenarios(2)
        self.assertEqual(len(all_scenarios), 16)
        for s in all_scenarios:
            self.assertEqual(len(s.credential_states), 2)
        # Check that the scenarios are unique
        self.assertEqual(len(set(all_scenarios)), 16)

        all_scenarios = generate_all_scenarios(3)
        self.assertEqual(len(all_scenarios), 64)
        for s in all_scenarios:
            self.assertEqual(len(s.credential_states), 3)

class WorseOrEqual(unittest.TestCase) :
    def test_credential_states(self):
        # first is theft
        self.assertTrue(worse_or_equal(St.THEFT, St.LEAKED))
        self.assertTrue(worse_or_equal(St.THEFT, St.THEFT))
        self.assertTrue(worse_or_equal(St.THEFT, St.LOST))
        self.assertTrue(worse_or_equal(St.THEFT, St.SAFE))

        # first is lost
        self.assertFalse(worse_or_equal(St.LOST, St.THEFT))
        self.assertFalse(worse_or_equal(St.LOST, St.LEAKED))
        self.assertTrue(worse_or_equal(St.LOST, St.LOST))
        self.assertTrue(worse_or_equal(St.LOST, St.SAFE))

        self.assertFalse(worse_or_equal(St.LEAKED, St.THEFT))
        self.assertTrue(worse_or_equal(St.LEAKED, St.LEAKED))
        self.assertFalse(worse_or_equal(St.LEAKED, St.LOST))
        self.assertTrue(worse_or_equal(St.LEAKED, St.SAFE))

        self.assertFalse(worse_or_equal(St.SAFE, St.THEFT))
        self.assertFalse(worse_or_equal(St.SAFE, St.LEAKED))
        self.assertFalse(worse_or_equal(St.SAFE, St.LOST))
        self.assertTrue(worse_or_equal(St.SAFE, St.SAFE))

    def test_worse_scenarios(self):
        better_scenario = Scenario(3, [St.SAFE, St.SAFE, St.THEFT])
        worse_scenarios = [
            Scenario(3, [St.SAFE, St.LEAKED, St.THEFT]), 
            Scenario(3, [St.SAFE, St.LOST, St.THEFT]), 
            Scenario(3, [St.SAFE, St.THEFT, St.THEFT]), 
            Scenario(3, [St.LEAKED, St.SAFE, St.THEFT]),
            Scenario(3, [St.LEAKED, St.LOST, St.THEFT]),
        ]
        for scenario in worse_scenarios:
            self.assertTrue(scenario.worse_or_equal(better_scenario))
            self.assertFalse(better_scenario.worse_or_equal(scenario))

    def test_unclear_scenarios(self):
        scenario1 = Scenario(3, [St.SAFE, St.SAFE, St.THEFT])
        unclear_scenarios = [
            Scenario(3, [St.SAFE, St.LEAKED, St.SAFE]), 
            Scenario(3, [St.SAFE, St.LOST, St.LEAKED]), 
            Scenario(3, [St.SAFE, St.THEFT, St.LOST]), 
            Scenario(3, [St.LEAKED, St.SAFE, St.SAFE]),
            Scenario(3, [St.LEAKED, St.LOST, St.SAFE]),
        ]
        for scenario in unclear_scenarios:
            self.assertFalse(scenario.worse_or_equal(scenario1))
            self.assertFalse(scenario1.worse_or_equal(scenario))
        # Complement must be worse or equal
        scenario2 = complement(scenario1)
        self.assertFalse(scenario2.worse_or_equal(scenario1))
        self.assertFalse(scenario1.worse_or_equal(scenario2))
    
    def test_compatible_scenarios(self):
        s1 = Scenario(3, [St.SAFE, St.SAFE, St.THEFT])
        s2 = Scenario(3, [St.LOST, St.LEAKED, St.SAFE])
        self.assertTrue(complement(s2).worse_or_equal(s1))
        self.assertFalse(can_coexist_in_profile(s1, s2))

        # Corner case: same scenario
        self.assertTrue(can_coexist_in_profile(s1, s1))

        s1 = Scenario(3, [St.LEAKED, St.SAFE, St.THEFT])
        s2 = Scenario(3, [St.SAFE, St.THEFT, St.SAFE])
        self.assertTrue(complement(s2).worse_or_equal(s1))
        self.assertFalse(can_coexist_in_profile(s1, s2))

class TestScenarios(unittest.TestCase):
    def test_is_complement(self):
        s1 = Scenario(3, [St.THEFT, St.LEAKED, St.SAFE])
        s2 = Scenario(3, [St.SAFE, St.LEAKED, St.THEFT])
        self.assertTrue(s1.is_complement(s2))
    
    def test_complement(self):
        s1 = Scenario(3, [St.THEFT, St.SAFE, St.SAFE])
        s2 = Scenario(3, [St.SAFE, St.LEAKED, St.LOST])
        
        c1 = complement(s1)
        c2 = complement(s2)
        
        self.assertEqual(c1.credential_states, [St.SAFE, St.THEFT, St.THEFT])
        self.assertEqual(c2.credential_states, [St.THEFT, St.LEAKED, St.LOST])
    
    def test_generate_all_scenarios(self):
        all_scenarios = generate_all_scenarios(2)
        self.assertEqual(len(all_scenarios), 16)
        for s in all_scenarios:
            self.assertEqual(len(s.credential_states), 2)

        all_scenarios = generate_all_scenarios(3)
        self.assertEqual(len(all_scenarios), 64)
        for s in all_scenarios:
            self.assertEqual(len(s.credential_states), 3)
    
    def test_is_special(self):
        s1 = Scenario(3, [St.THEFT, St.LEAKED, St.SAFE])
        s2 = Scenario(3, [St.SAFE, St.LEAKED, St.THEFT])
        s3 = Scenario(3, [St.LEAKED, St.THEFT, St.SAFE])
        s4 = Scenario(3, [St.SAFE, St.SAFE, St.SAFE])
        
        self.assertTrue(is_special(s1))
        self.assertTrue(is_special(s2))
        self.assertTrue(is_special(s3))
        self.assertFalse(is_special(s4))

class TestWellDefinedRules(unittest.TestCase):
    def test_priority_mechanism_is_rule_well_defined(self):
        # Test cases for PriorityMechanism        
        pm = PriorityMechanism([0, 1, 2], False)
        self.assertTrue(pm.is_rule_well_defined())
        # Next line throws an exception, so catch it
        try:
            pm = PriorityMechanism([2, 4, 1, 3], True)
        except Exception as e:
            self.assertEqual(str(e), "Rule ([2, 4, 1, 3]) is not well defined")

    def test_hierarchical_mechanism_is_rule_well_defined(self):
        # Test cases for HierarchicalMechanism
        hm = HierarchicalMechanism(3, [[0, 1], [3, 2]], None)
        self.assertTrue(hm.is_rule_well_defined())
        hm = HierarchicalMechanism(9, [[0, 1, 8], [3, 2], [4, 5], [7, 6]], None)
        self.assertTrue(hm.is_rule_well_defined())

        # Next line throws an exception, so catch it
        try:
            hm = HierarchicalMechanism(3, [[0, 1], [1, 2]], None)
        except Exception as e:
            self.assertEqual(str(e), "Rule ([[0, 1], [1, 2]]) is not well defined")
        try:
            hm = HierarchicalMechanism(3, [[0, 1], [1, 3]], None)
        except Exception as e:
            self.assertEqual(str(e), "Rule ([[0, 1], [1, 3]]) is not well defined")


class TestPriorityMechanisms(unittest.TestCase):
    def test_priority(self):
        # decider_one
        s1 = Scenario(4, [St.SAFE, St.SAFE, St.THEFT, St.THEFT])
        s2 = Scenario(4, [St.SAFE, St.LOST, St.SAFE, St.THEFT])
        s3 = Scenario(4, [St.THEFT, St.SAFE, St.LEAKED, St.SAFE])
        # decider_two
        s4 = Scenario(4, [St.LEAKED, St.SAFE, St.THEFT, St.THEFT])
        # decider_three
        s5 = Scenario(4, [St.LOST, St.LEAKED, St.SAFE, St.THEFT])
        # PRE case
        s6 = Scenario(4, [St.LOST, St.LOST, St.SAFE, St.THEFT])

        m = PriorityMechanism([0, 1, 2, 3], False)
        self.assertTrue(m.succeeds(s1))
        self.assertTrue(m.succeeds(s2))
        self.assertFalse(m.succeeds(s3))
        self.assertTrue(m.succeeds(s4))
        self.assertTrue(m.succeeds(s5))
        self.assertTrue(m.succeeds(s6))
    
    def test_profile_two_creds(self):
        m = PriorityMechanism([0, 1], False)
        profile = m.profile()
        self.assertEqual(len(profile), 6)
        self.assertEqual(set(profile), set([
            Scenario(2, [St.SAFE, St.SAFE]),
            Scenario(2, [St.SAFE, St.LEAKED]),
            Scenario(2, [St.SAFE, St.LOST]),
            Scenario(2, [St.SAFE, St.THEFT]),
            Scenario(2, [St.LEAKED, St.SAFE]),
            Scenario(2, [St.LOST, St.SAFE]),
        ]))

        m = PriorityMechanism([1, 0], False)
        profile = m.profile()
        self.assertEqual(len(profile), 6)
        self.assertEqual(set(profile), set([
            Scenario(2, [St.SAFE, St.SAFE]),
            Scenario(2, [St.LEAKED, St.SAFE]),
            Scenario(2, [St.LOST, St.SAFE]),
            Scenario(2, [St.THEFT, St.SAFE]),
            Scenario(2, [St.SAFE, St.LEAKED]),
            Scenario(2, [St.SAFE, St.LOST]),
        ]))
    
    def test_profile_three_creds(self):
        m = PriorityMechanism([0, 1, 2], False)
        profile = m.profile()
        self.assertEqual(len(profile), 28) # (4^3 - 2^3) / 2 = 28
        self.assertEqual(set(profile), set([
            # All 16 scenarios where the first credential is safe
            Scenario(3, [St.SAFE, St.SAFE, St.SAFE]),
            Scenario(3, [St.SAFE, St.SAFE, St.LEAKED]),
            Scenario(3, [St.SAFE, St.SAFE, St.LOST]),
            Scenario(3, [St.SAFE, St.SAFE, St.THEFT]),
            Scenario(3, [St.SAFE, St.LEAKED, St.SAFE]),
            Scenario(3, [St.SAFE, St.LEAKED, St.LEAKED]),
            Scenario(3, [St.SAFE, St.LEAKED, St.LOST]),
            Scenario(3, [St.SAFE, St.LEAKED, St.THEFT]),
            Scenario(3, [St.SAFE, St.LOST, St.SAFE]),
            Scenario(3, [St.SAFE, St.LOST, St.LEAKED]),
            Scenario(3, [St.SAFE, St.LOST, St.LOST]),
            Scenario(3, [St.SAFE, St.LOST, St.THEFT]),
            Scenario(3, [St.SAFE, St.THEFT, St.SAFE]),
            Scenario(3, [St.SAFE, St.THEFT, St.LEAKED]),
            Scenario(3, [St.SAFE, St.THEFT, St.LOST]),
            Scenario(3, [St.SAFE, St.THEFT, St.THEFT]),
            # All 4 scenarios where the first credential is leaked but second is safe
            Scenario(3, [St.LEAKED, St.SAFE, St.SAFE]),
            Scenario(3, [St.LEAKED, St.SAFE, St.LEAKED]),
            Scenario(3, [St.LEAKED, St.SAFE, St.LOST]),
            Scenario(3, [St.LEAKED, St.SAFE, St.THEFT]),
            # All 4 scenarios where the first credential is lost but second is safe
            Scenario(3, [St.LOST, St.SAFE, St.SAFE]),
            Scenario(3, [St.LOST, St.SAFE, St.LEAKED]),
            Scenario(3, [St.LOST, St.SAFE, St.LOST]),
            Scenario(3, [St.LOST, St.SAFE, St.THEFT]),
            # first two credentials are leaked / lost, third is safe
            Scenario(3, [St.LEAKED, St.LEAKED, St.SAFE]),
            Scenario(3, [St.LEAKED, St.LOST, St.SAFE]),
            Scenario(3, [St.LOST, St.LEAKED, St.SAFE]),
            Scenario(3, [St.LOST, St.LOST, St.SAFE]),
        ]))

class TestPREMechanisms(unittest.TestCase):    
    def test_priority_with_exception(self):
        # decider_one
        s1 = Scenario(4, [St.SAFE, St.SAFE, St.THEFT, St.THEFT])
        s2 = Scenario(4, [St.SAFE, St.LOST, St.SAFE, St.THEFT])
        s3 = Scenario(4, [St.THEFT, St.SAFE, St.LEAKED, St.SAFE])
        # decider_two
        s4 = Scenario(4, [St.LEAKED, St.SAFE, St.THEFT, St.THEFT])
        # decider_three
        s5 = Scenario(4, [St.LOST, St.LEAKED, St.SAFE, St.THEFT])

        m = PriorityMechanism([0, 1, 2, 3], True)
        self.assertTrue(m.succeeds(s1))
        self.assertTrue(m.succeeds(s2))
        self.assertFalse(m.succeeds(s3))
        self.assertTrue(m.succeeds(s4))
        self.assertTrue(m.succeeds(s5))

        s6 = Scenario(4, [St.LOST, St.LOST, St.SAFE, St.THEFT])
        self.assertFalse(m.succeeds(s6))

class TestTieBreaks(unittest.TestCase):
    def test_generate_tie_break_inputs(self):
        # one credential
        all_possible_inputs = generate_tie_break_inputs([0])
        self.assertEqual(all_possible_inputs, [])

        # two credentials
        all_possible_inputs = generate_tie_break_inputs([0, 1])
        self.assertEqual(all_possible_inputs, [([0], [1])])

        all_possible_inputs = generate_tie_break_inputs([1, 2])
        self.assertEqual(all_possible_inputs, [([1], [2])])

        # three credentials
        all_possible_inputs = generate_tie_break_inputs([0, 1, 2])
        self.assertEqual(all_possible_inputs, [
            ([0], [1]), ([0], [2]), ([1], [2]), ([0, 1], [0, 2]), ([0, 1], [1, 2]), ([0, 2], [1, 2])
        ])

class TestMajorityMechanisms(unittest.TestCase):
    def test_majority_two_creds(self):
        t = lambda x, y: uniform_priority_tie_breaker(x, y, [0, 1])
        m = MajorityMechanism(2, t)
        p = m.profile()
        self.assertEqual(len(p), 6)
        self.assertEqual(set(p), set([
            Scenario(2, [St.SAFE, St.SAFE]),
            Scenario(2, [St.SAFE, St.LEAKED]),
            Scenario(2, [St.SAFE, St.LOST]),
            Scenario(2, [St.SAFE, St.THEFT]),
            Scenario(2, [St.LEAKED, St.SAFE]),
            Scenario(2, [St.LOST, St.SAFE]),
        ]))
    
    def test_majority_three_creds(self):
        t = lambda x, y: uniform_priority_tie_breaker(x, y, [0, 1, 2])
        m = MajorityMechanism(3, t)
        p = m.profile()
        self.assertEqual(len(p), 28)
        self.assertEqual(set(p), set([
            # All 10 scenarios where 2-of-3 credentials are safe
            Scenario(3, [St.SAFE, St.SAFE, St.SAFE]),
            Scenario(3, [St.SAFE, St.SAFE, St.LEAKED]),
            Scenario(3, [St.SAFE, St.SAFE, St.LOST]),
            Scenario(3, [St.SAFE, St.SAFE, St.THEFT]),
            Scenario(3, [St.SAFE, St.LEAKED, St.SAFE]),
            Scenario(3, [St.SAFE, St.LOST, St.SAFE]),
            Scenario(3, [St.SAFE, St.THEFT, St.SAFE]),
            Scenario(3, [St.LEAKED, St.SAFE, St.SAFE]),
            Scenario(3, [St.LOST, St.SAFE, St.SAFE]),
            Scenario(3, [St.THEFT, St.SAFE, St.SAFE]),
            # All 12 scenarios where one is safe, rest two are not stolen
            Scenario(3, [St.SAFE, St.LEAKED, St.LEAKED]),
            Scenario(3, [St.SAFE, St.LOST, St.LEAKED]),
            Scenario(3, [St.SAFE, St.LEAKED, St.LOST]),
            Scenario(3, [St.SAFE, St.LOST, St.LOST]),
            Scenario(3, [St.LEAKED, St.SAFE, St.LEAKED]),
            Scenario(3, [St.LOST, St.SAFE, St.LEAKED]),
            Scenario(3, [St.LEAKED, St.SAFE, St.LOST]),
            Scenario(3, [St.LOST, St.SAFE, St.LOST]),
            Scenario(3, [St.LEAKED, St.LEAKED, St.SAFE]),
            Scenario(3, [St.LOST, St.LEAKED, St.SAFE]),
            Scenario(3, [St.LEAKED, St.LOST, St.SAFE]),
            Scenario(3, [St.LOST, St.LOST, St.SAFE]),
            # All 6 scenarios where one is stolen, one is safe, but the tie breaker is needed
            Scenario(3, [St.SAFE, St.THEFT, St.LEAKED]),
            Scenario(3, [St.SAFE, St.THEFT, St.LOST]),
            Scenario(3, [St.SAFE, St.LEAKED, St.THEFT]),
            Scenario(3, [St.SAFE, St.LOST, St.THEFT]),
            Scenario(3, [St.LEAKED, St.SAFE, St.THEFT]),
            Scenario(3, [St.LOST, St.SAFE, St.THEFT]),
        ]))
    
    def test_diff_tie_breaks(self):
        all_tie_breaks = generate_all_binary_tuples(6)
        self.assertEqual(len(all_tie_breaks), 2**6)
        for tb in all_tie_breaks:
            m = MajorityMechanism(3, lambda x, y: tie_breaker_function_3creds(x, y, tb))
            p = m.profile()
            self.assertEqual(len(p), 28)

        m1 = MajorityMechanism(3, lambda x, y: tie_breaker_function_3creds(x, y, all_tie_breaks[0]))
        m2 = MajorityMechanism(3, lambda x, y: tie_breaker_function_3creds(x, y, all_tie_breaks[1]))
        self.assertNotEqual(m1.profile(), m2.profile())

        # # Priority tie-breaks
        # # All permutations of vectors of length 3 with elements 0, 1, 2
        # perms = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]
        # for priority in perms:
        #     m = MajorityMechanism(3, lambda x, y: uniform_priority_tie_breaker(x, y, priority))
        #     p = m.profile()
        #     self.assertEqual(len(p), 28)

        # # Different priority tie-breaks for 1-length and 2-length vectors
        # for priority1 in perms:
        #     for priority2 in perms:
        #         priority = [priority1, priority2]
        #         m = MajorityMechanism(3, lambda x, y: different_priority_tie_breaker(x, y, priority))
        #         self.assertEqual(len(m.profile()), 28)        

class TestHierarchicalMechanisms(unittest.TestCase):
    # also tests utils.compositions
    def test_generate_all_hierarchies(self):
        all_compositions = utils.compositions(3)
        self.assertEqual(len(all_compositions), 4)
        self.assertEqual(all_compositions, [[1, 1, 1], [1, 2], [2, 1], [3]])

        expected_lengths = [1, 2, 4, 8, 16]
        for length in range(5):
            self.assertEqual(len(utils.compositions(length + 1)), expected_lengths[length])
            self.assertEqual(len(HierarchicalMechanism.generate_all_hierarchies(length + 1)), expected_lengths[length])

        all_hierarchies = HierarchicalMechanism.generate_all_hierarchies(3)
        self.assertEqual(all_hierarchies, [
            [[0], [1], [2]],
            [[0], [1, 2]],
            [[0, 1], [2]],
            [[0, 1, 2]]
        ])

    def test_tie_break_inputs_for_hm(self):
        C = [0]
        self.assertEqual(len(tie_break_inputs_for_hm(C)), 2) # 2*1 C 1
        C = [0, 1]
        self.assertEqual(len(tie_break_inputs_for_hm(C)), 6) # 2*2 C 2
        self.assertEqual(tie_break_inputs_for_hm(C), [
            ((), ()),
            ((0,), (0,)),
            ((0,), (1,)),
            ((1,), (0,)),
            ((1,), (1,)),
            ((0, 1), (0, 1))
        ])
        C = [0, 1, 2]
        self.assertEqual(len(tie_break_inputs_for_hm(C)), 20) # 2*3 C 3
        C = [0, 1, 2, 3]
        self.assertEqual(len(tie_break_inputs_for_hm(C)), 70) # 2*4 C 4
    
    def test_all_ties_to_break(self):
        rule = [[0], [1]]
        all_possible_inputs = all_ties_to_break(rule)
        self.assertEqual(len(all_possible_inputs), 0)
        self.assertEqual(HierarchicalMechanism.number_of_tie_breaks([1, 1]), 0)
        
        rule = [[0, 1], [2]]
        all_possible_inputs = all_ties_to_break(rule)
        self.assertEqual(len(all_possible_inputs), 2)
        self.assertEqual(all_possible_inputs, [([0], [1]), ([0, 2], [1, 2])])
        self.assertEqual(HierarchicalMechanism.number_of_tie_breaks([2, 1]), 2)

        rule = [[0, 2, 3], [1], [4, 5, 6]]
        self.assertEqual(HierarchicalMechanism.number_of_tie_breaks([3, 1, 3]), 336)
        all_possible_inputs = all_ties_to_break(rule)
        self.assertEqual(len(all_possible_inputs), 336)

    def test_three_creds(self):
        three_cred_majority_profiles = get_all_majority_profiles()
        three_cred_priority_profiles = get_all_priority_profiles()

        tie_breaks = generate_all_binary_tuples(2)
        # HM with two creds at L2 and one at L1
        for tb in tie_breaks:
            # print("Hierarchical 2-1 with tie breaker", tb)
            all_possible_inputs = [([0], [1])] + [([0, 2], [1, 2])]
            hm = HierarchicalMechanism(3, [[0, 1], [2]], lambda x, y: break_ties(x, y, all_possible_inputs, tb))
            p = hm.profile()
            self.assertEqual(len(p), 28)
            # assert that its profile is equal to some majority mechanism
            x = [(label, p1) for (label, p1) in three_cred_majority_profiles if p1 == p]
            self.assertEqual(len(x), 1)
            # print(x[0][0])

        # HM with two creds at L1 and one at L2
        for tb in tie_breaks:
            # print("Hierarchical 1-2 with tie breaker", tb)
            all_possible_inputs = [([0], [1])] + [([0, 2], [1, 2])]
            hm = HierarchicalMechanism(3, [[2], [0, 1]], lambda x, y: break_ties(x, y, all_possible_inputs, tb))
            p = hm.profile()
            self.assertEqual(len(p), 28)
            x = [(label, p1) for (label, p1) in three_cred_priority_profiles if p1 == p]
            self.assertEqual(len(x), 1)
            # print(x[0][0])

    def test_all_two_cred_profiles(self):
        hm_profiles = HierarchicalMechanism.get_all_profiles(2)
        self.assertEqual(len(hm_profiles), HierarchicalMechanism.number_of_hierarchical_mechanisms(2))
        unique_profiles = remove_duplicates(hm_profiles)
        self.assertEqual(len(unique_profiles), 2)

    def test_all_three_cred_profiles(self):
        hm_profiles = HierarchicalMechanism.get_all_profiles(3)
        self.assertEqual(len(hm_profiles), HierarchicalMechanism.number_of_hierarchical_mechanisms(3))
        profiles = get_all_3cred_profiles()
        for (label, profile) in hm_profiles:
            x = [(label2, p) for (label2, p) in profiles if p == profile]
            self.assertEqual(len(x), 1)
            # print(label, x[0][0])
    
    def test_all_four_cred_profiles(self):
        hm_profiles = HierarchicalMechanism.get_all_profiles(4)
    
    # def test_check_growth_rate_maj_and_hm(self):
    #     for i in range(1, 9):
    #         x = HierarchicalMechanism.number_of_hierarchical_mechanisms(i)
    #         y = MajorityMechanism.number_of_majority_mechanisms(i)
    #         print(i, x, y, x - y)

if __name__ == '__main__':
    unittest.main()
