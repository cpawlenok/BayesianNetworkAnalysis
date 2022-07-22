import copy
import json
import math
import Factor as F

def getBinaryList(num, length):
    index = num
    tempBinary = []
    binary = [0]*(length)
    if num == 0:
        return binary
    else:
        # create list of binary digits
        while index > 0:
            temp = int(float(index % 2))
            tempBinary.append(temp)
            index = int(index/2)

        # reverse list to match our parent node order
        for i in range(len(tempBinary)):
            binary[i] = tempBinary[i]

        binary = [ele for ele in reversed(binary)]

    return binary

# Collects dictionary serialized into JSON file
def collectJSON(JSONFile):
    with open(JSONFile) as file:
        network = json.load(file)
    return network

def clearSheet(WB, fileName):
    ws3 = WB["Sheet3"]
    ws3.delete_rows(1, ws3.max_row + 1)
    WB.save(fileName)

def outputModel(modelData, WB, fileName, headers):
    # print("This is being accessed correctly")
    currentSheet = WB["Sheet3"]
    if currentSheet.cell(column=1, row=1).value == None:
        currentSheet.cell(column=1, row=1).value = "ModelNum"
        currentSheet.cell(column=2, row=1).value = "ScenarioNum"
        columnIndex = 3

        for header in headers:
            currentSheet.cell(column=columnIndex, row=1).value = header
            columnIndex+=1

    modelNum = 0
    for scenarios in modelData:
        rowIndex = 2 + ((len(modelData[0])) * (modelNum))
        for scenario in scenarios:
            # print(scenario)
            currentSheet.cell(column=1, row=rowIndex).value = modelNum
            currentSheet.cell(column=2, row=rowIndex).value = scenarios.index(scenario)
            currColumn = 3
            for entry in scenario:
                currentSheet.cell(column=currColumn, row=rowIndex).value = entry
                currColumn+=1
            rowIndex+=1
        modelNum+=1
    WB.save(fileName)

# runs variable elimination and outputs models to excel
# accepts actions array, experiment object, dictionary of factors, and True for Min model or False for Max model
# note: each model is defined by
#           - set of scenarios
#           - same node set to min or max value
def runModels(actions, experiment, factorDict, MIN):
    keys = factorDict.keys()
    row = []
    model = []
    fullModelData = []

    if MIN:
        setProb = 0.0
    else:
        setProb = 1.0

    scenarios = 2**len(actions)
    evidence = True

    # for each node set to base case
    for baseEvidence in keys:

        # check if evidence is an action node
        # if evidence is an action node, skip this model
        for action in actions:
            if baseEvidence == action:
                evidence = False

        if evidence:
            for scenario in range(scenarios):
                sequence = getBinaryList(scenario, len(actions))
                for q in keys:
                    evidenceData = (baseEvidence, setProb)
                    actionData = (actions, sequence)
                    test = F.Factors(factorDict, query=q, evidenceData=evidenceData, actionData=actionData)
                    row.append(test.runVariableElimination().CPTValues[1])

                # add row to model
                model.append(row)
                row = []

            # add full set of scenarios to modelData array
            fullModelData.append(model)
            model = []

        evidence = True

    # Output models to correct excel doc for min or max models
    if MIN:
        clearSheet(experiment.minWB, experiment.minFile)
        outputModel(fullModelData, experiment.minWB, experiment.minFile, keys)
        experiment.minWB.save(experiment.minFile)
    else:
        clearSheet(experiment.maxWB, experiment.maxFile)
        outputModel(fullModelData, experiment.maxWB, experiment.maxFile, keys)
        experiment.maxWB.save(experiment.maxFile)

results = []
tempDict = {}

def runNoEvidenceModel(actions, experiment, factorDict):
    keys = factorDict.keys()
    row = []
    model = []
    fullModelData = []
    scenarios = 2**len(actions)
    evidence = "no evidence"

    for scenario in range(scenarios):
        sequence = getBinaryList(scenario, len(actions))
        for q in keys:
            evidenceData = (evidence, 0.0)
            actionData = (actions, sequence)
            test = F.Factors(factorDict, query=q, evidenceData=evidenceData, actionData=actionData)
            row.append(test.runVariableElimination().CPTValues[1])

        # add row to model
        model.append(row)
        row = []
    fullModelData.append(model)

    clearSheet(experiment.ogWB, experiment.fileName)
    outputModel(fullModelData, experiment.ogWB, experiment.fileName, keys)
    experiment.ogWB.save(experiment.fileName)



def startElim(filepath, experiment, actions):
    factorDict = collectJSON(filepath)

    runModels(actions, experiment, factorDict, True)
    runModels(actions, experiment, factorDict, False)
    runNoEvidenceModel(actions, experiment, factorDict)

    return