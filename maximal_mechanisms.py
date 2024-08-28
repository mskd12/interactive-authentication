from scenarios import St

# Models both priority and priority with exception mechanisms
class PriorityMechanism:
    # A priority mechanism is defined by a rule and whether an exception applies
    def __init__(self, rule: [int], exception: bool):
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
        credentials = scenario.credentials
        for x in self.rule:
            if credentials[x] == St.SAFE:
                return True # User wins
            elif credentials[x] == St.THEFT:
                return False # Attacker wins
        return False # Corner case (no safe, theft)

    def priority_with_exception_judging_function(self, scenario):
        rule = self.rule
        credentials = scenario.credentials
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


# def success(mechanism, scenario):
#     if mechanism == Mechanism.PRIORITY:
#         return scenario.priority_rule(mechanism.rule)
#     elif mechanism == Mechanism.MAJORITY:
#         return scenario.majority_rule()
#     else:
#         raise Exception("Mechanism %s not supported" % (mechanism,))