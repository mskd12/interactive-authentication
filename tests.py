from scenarios import *
from maximal_mechanisms import *

import unittest

class WorseOrEqual(unittest.TestCase) :
    def test_credential_states(self):
        worse_or_equal(St.THEFT, St.THEFT) == True
        worse_or_equal(St.THEFT, St.LEAKED) == True
        worse_or_equal(St.THEFT, St.LOST) == True
        worse_or_equal(St.THEFT, St.SAFE) == True

        worse_or_equal(St.LEAKED, St.THEFT) == False
        worse_or_equal(St.LEAKED, St.LEAKED) == False
        worse_or_equal(St.LEAKED, St.LOST) == False
        worse_or_equal(St.LEAKED, St.SAFE) == True

        worse_or_equal(St.SAFE, St.THEFT) == False
        worse_or_equal(St.SAFE, St.LEAKED) == False
        worse_or_equal(St.SAFE, St.LOST) == False
        worse_or_equal(St.SAFE, St.SAFE) == False

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
            scenario.worse_or_equal(better_scenario) == True
            better_scenario.worse_or_equal(scenario) == False

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
            scenario.worse_or_equal(scenario1) == False
            scenario1.worse_or_equal(scenario) == False
        # Complement must be worse or equal
        scenario2 = complement(scenario1)
        scenario2.worse_or_equal(scenario1) == False
        scenario1.worse_or_equal(scenario2) == False

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
        
        self.assertEqual(c1.credentials, [St.SAFE, St.THEFT, St.THEFT])
        self.assertEqual(c2.credentials, [St.THEFT, St.LEAKED, St.LOST])
    
    def test_generate_all_scenarios(self):
        all_scenarios = generate_all_scenarios(2)
        self.assertEqual(len(all_scenarios), 16)
        for s in all_scenarios:
            self.assertEqual(len(s.credentials), 2)

        all_scenarios = generate_all_scenarios(3)
        self.assertEqual(len(all_scenarios), 64)
        for s in all_scenarios:
            self.assertEqual(len(s.credentials), 3)
    
    def test_is_special(self):
        s1 = Scenario(3, [St.THEFT, St.LEAKED, St.SAFE])
        s2 = Scenario(3, [St.SAFE, St.LEAKED, St.THEFT])
        s3 = Scenario(3, [St.LEAKED, St.THEFT, St.SAFE])
        s4 = Scenario(3, [St.SAFE, St.SAFE, St.SAFE])
        
        self.assertTrue(is_special(s1))
        self.assertTrue(is_special(s2))
        self.assertTrue(is_special(s3))
        self.assertFalse(is_special(s4))

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


if __name__ == '__main__':
    unittest.main()
