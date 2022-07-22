import variableElimination as ve
class Factors:
    # create the network Factors
    # query variable - variable we are trying to find, given as a string
    # evidenceData - variable that is known, given as a tuple defined (Evidence Node, Probability of Evidence Node)
    # actionData is a tuple defined (List of Actions, Binary Sequence of Actions)
    def __init__(self, factorDict, query, evidenceData, actionData):
        self.factorDict = factorDict
        self.factors = self.getFactors()
        self.query = [query]
        self.setEvidence(evidenceData[0], evidenceData[1])
        self.setActions(actionData)

    # creates a factor
    # unconditioned variables = node
    # conditioned variables = parents
    class factor:
        def __init__(self, conditioned, unconditioned, CPTValues):
            # node = conditioned variable for factors
            # parents = unconditioned variables for factors
            # ordered so that CPTValues line up correctly with parents through Pythia
            if len(conditioned) == 0:
                self.conditioned = []
            else:
                self.conditioned = [conditioned]
            self.unconditioned = unconditioned
            self.CPTValues = CPTValues

    # Searches the network for the evidence
    # Calls overwriteCPT to set the CPTValues of evidence node = evidenceProb
    def setEvidence(self, node, probability):
        for factor in self.factors:
            for nodeName in factor.conditioned:
                if nodeName == node:
                    index = factor.conditioned.index(node)
                    self.overwriteCPT(factor, probability, index)
                    return

            for nodeName in factor.unconditioned:
                if nodeName == node and len(factor.conditioned) == 0:
                    index = 0
                    self.overwriteCPT(factor, probability, index)
                    return

    def setActions(self, actionSequence):
        actions = actionSequence[0]
        sequence = actionSequence[1]

        for factor in self.factors:
            for nodeName in factor.conditioned:
                for action in actions:
                    if nodeName == action:
                        index = factor.conditioned.index(action)
                        probability = sequence[actions.index(action)]
                        factor.unconditioned = [nodeName]
                        factor.conditioned = []
                        factor.CPTValues = [1 - probability, probability]

            for nodeName in factor.unconditioned:
                for action in actions:
                    if nodeName == action and len(factor.conditioned) == 0:
                        index = 0
                        probability = sequence[actions.index(action)]
                        factor.unconditioned = [nodeName]
                        factor.conditioned = []
                        factor.CPTValues = [1 - probability, probability]

    # Accepts a node, probability and binary index of the node
    def overwriteCPT(self, factor, probability, index):
        binaryLength = len(factor.conditioned) + len(factor.unconditioned)

        for row in range(len(factor.CPTValues)):
            binList = ve.getBinaryList(row, binaryLength)
            if binList[index] == 1:
                factor.CPTValues[row] = probability
            else:
                factor.CPTValues[row] = 1.0 - probability
        return

    # Creates and returns list of type factor
    def getFactors(self):
        allFactors = self.factorDict
        keys = allFactors.keys()
        factors = []
        for key in keys:
            if allFactors[key]['Item1'] == None:
                nextFactor = self.factor([], [key], allFactors[key]['Item2'])

            else:
                nextFactor = self.factor(key, allFactors[key]['Item1'], allFactors[key]['Item2'])

            nextFactor = self.rectifyFactor(nextFactor)
            factors.append(nextFactor)
        return factors

    # considering the CPTs produced by pythia don't include false scenarios for nodes
    # rectifyFactor adds the false scenarios to the CPTValues
    # then returns the new factor
    def rectifyFactor(self, tFactor):
        newCPT = []
        if len(tFactor.conditioned) > 0:
            for i in range(len(tFactor.CPTValues)):
                newCPT.append(1.0 - tFactor.CPTValues[i])
        else:
            newCPT.append(1.0 - tFactor.CPTValues[0])
        tFactor.CPTValues = newCPT + tFactor.CPTValues
        return tFactor

    # Displays all current factors
    def printFactors(self):
        for factor in self.factors:
            print("node:", factor.conditioned)
            print("parents:", factor.unconditioned)
            print("values:", factor.CPTValues)
            print()
        print("__________________________________________________________")

    # Framework that structures the variable elimination loop
    # then calls the correct functions to perform variable elimination
    # returns probability(query node occurring)
    def runVariableElimination(self):

        # first we will join on the evidence variable
        # I know this is slight roundabout but this was to get the
        # now we can keep joining until the only variable left is the query variable
        done = self.checkQuery()
        factorToJoin = self.getNextUnconditioned()
        if done[0]:
            return self.factors[done[1]]
        self.factors.remove(factorToJoin)

        # main loop, does not stop until query node has be found and calculated
        # todo: change loop structure, we need to join all factors regardless of how many con. and uncon. variables
        while not done[0]:
            for currFactor in self.factors:
                for variable in currFactor.unconditioned:
                    if variable in factorToJoin.unconditioned:
                        #
                        newFactor = self.joinFactors(factorToJoin, currFactor, variable)
                        self.eliminate(newFactor, variable)

                        # this was a workaround for changing the list while still iterating over it
                        # removing or adding factors to the list we are iterating through causes indexing issues
                        currFactor.conditioned = newFactor.conditioned
                        currFactor.unconditioned = newFactor.unconditioned
                        currFactor.CPTValues = newFactor.CPTValues

                        done = self.checkQuery()
                        if done[0]:
                            self.normalize(self.factors[done[1]])
                            # print("Return Factor: ", self.factors[done[1]].CPTValues)
                            return self.factors[done[1]]

            factorToJoin = self.getNextUnconditioned()
            self.factors.remove(factorToJoin)

    # checks if factor is the query factor
    def checkQuery(self):
        done = False
        index = 0
        for checkFactor in self.factors:
            if len(checkFactor.conditioned) == 0 and checkFactor.unconditioned == self.query:
                done = True
                index = self.factors.index(checkFactor)

        return (done, index)

    def checkEvidence(self):
        # todo: check if evidence factor as a one variable factor
        return

    # returns first unconditioned variables in self.factors
    # I'm not sure how efficient this is
    def getNextUnconditioned(self):
        for nextFactor in self.factors:
            if len(nextFactor.conditioned) == 0:
                return nextFactor
        raise Exception("No unconditioned variables exist")

    # joins and eliminates - table entries only include node = 1 so no need for true elimination because we
    # only have half of the table
    # todo: confirm support for joining more complex factors
    def joinFactors(self, factorA, factorB, joinVariable):
        probList = [None] * len(factorB.CPTValues)
        variables = []
        factorAElements = len(factorA.CPTValues)
        factorBElements = len(factorB.CPTValues)
        joinIndex = factorB.unconditioned.index(joinVariable) + len(factorB.conditioned)
        for i in range(factorAElements):
            for j in range(factorBElements):
                digitAtIndex = ve.getBinaryList(j, len(factorB.unconditioned) + len(factorB.conditioned))
                if i == digitAtIndex[joinIndex]:
                    probList[j] = factorA.CPTValues[i] * factorB.CPTValues[j]

        if len(factorB.unconditioned) > 1:
            # for variable in variables:
            #     if variable == joinVariable:
            #         variables.pop(variables.index(variable))

            # Add all variables to the new unconditioned factor
            for var in factorB.unconditioned:
                variables.append(var)

            newFactor = self.factor(factorB.conditioned[0], variables, probList)
        else:
            # Add all variables to the new unconditioned factor
            for var in factorB.conditioned:
                variables.append(var)

            for var in factorB.unconditioned:
                variables.append(var)
            newFactor = self.factor([], variables, probList)
        return newFactor

    # todo: confirm support for eliminating more complex factors
    def eliminate(self, factor, variable):
        newProbs = []
        numCPTRows = len(factor.CPTValues)
        binLength = len(factor.conditioned) + len(factor.unconditioned)
        index = factor.unconditioned.index(variable) + len(factor.conditioned)
        # "+ length of conditioned" shifts right to account for conditioned variables
        for i in range(int(numCPTRows)):
            rowBinary = ve.getBinaryList(i, binLength)
            for j in range(i, numCPTRows):
                nextRowBinary = ve.getBinaryList(j, binLength)
                comparison = []
                for item1, item2 in zip(rowBinary, nextRowBinary):
                    comparison.append(abs(item1 - item2))
                if sum(comparison) == 1 and comparison[index] == 1:
                    # print("added : ",
                    #       rowBinary,
                    #       nextRowBinary)
                    newProbs.append(factor.CPTValues[i] + factor.CPTValues[j])

        if len(factor.unconditioned) > 1:
            factor.unconditioned.remove(variable)
        else:
            factor.conditioned.remove(variable)
        factor.CPTValues = newProbs

    def normalize(self, factor):
        probSum = sum(factor.CPTValues)
        for i in range(len(factor.CPTValues)):
            factor.CPTValues[i] = factor.CPTValues[i] / probSum