import json

class Factors:
    # create the network Factors

    def __init__(self, filePath):
        self.factorDict = collectJSON(filePath)
        self.factors = self.getFactors()

    # creates a factor
    # unconditioned variables = node
    # conditioned variables = parents
    class factor:
        def __init__(self, currentNode, dict):
            self.node = currentNode
            self.parents = dict[currentNode]['Item1']
            self.CPTValues = dict[currentNode]['Item2']

    def getFactors(self):
        allFactors = self.factorDict
        keys = allFactors.keys()
        factors = []
        for key in keys:
            newFactor = self.factor(key, allFactors)
            factors.append(newFactor)
        return factors

    def printFactors(self):
        for factor in self.factors:
            print("node:", factor.node)
            print("parents:", factor.parents)
            print("values:", factor.CPTValues)



def collectJSON(JSONFile):
    with open(JSONFile) as file:
        network = json.load(file)
    return network



