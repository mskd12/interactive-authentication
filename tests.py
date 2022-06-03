from complete_set_size import *

import unittest

class WorseOrEqual(unittest.TestCase) :
    def test_credentials(self):
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


if __name__ == '__main__':
    unittest.main()
