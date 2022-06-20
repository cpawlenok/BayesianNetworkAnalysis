# takes three excel documents and the target node
# calculates expected value of perfect information (EVPI) for each node
# returns EVPI array and array of which scenarios resulted in maximum expected values
def getEVPI(ogWB, minWB, maxWB, termnode):
    marginalSheet = ogWB["Sheet2"]
    baseWS = ogWB["Sheet3"]
    minWS = minWB["Sheet3"]
    maxWS = maxWB["Sheet3"]

    EVPIs = []
    marginals = []
    scenarios = [0] * 16
    modelBase = 2
    scenarioNum = 0
    EStar, maxExpected, minExpected = [-1] * 3

    # get marginal probabilities
    for row in marginalSheet.iter_rows(min_row=2, min_col=2, max_col=2, values_only=True):
        marginals.append(row[0])

    # get max avoiding famine value (E*) from base case sheet
    for row in baseWS.iter_rows(min_row=2, min_col=termnode, max_col=termnode, values_only=True):
        if row[0] > EStar:
            EStar = row[0]

    # main loop
    for i in range(len(marginals)):

        # find max expected value from max sheet and which scenario resulted in that value
        for row in maxWS.iter_rows(min_row=modelBase, max_row=modelBase+15, min_col=2, max_col=termnode, values_only=True):
            if row[-1] > maxExpected:
                maxExpected = row[-1]
                scenarioNum = row[0]
        scenarios[scenarioNum] += 1

        # find max expected value from min sheet and which scenario resulted in that value
        for row in minWS.iter_rows(min_row=modelBase, max_row=modelBase + 15, min_col=2, max_col=termnode, values_only=True):
            if row[-1] > minExpected:
                minExpected = row[-1]
                scenarioNum = row[0]
        scenarios[scenarioNum] += 1

        # calculate EVPI(X) = |E* - sum( P(Xa) * max(E(Xa)) )|
        EVPIs.append(abs(EStar - ((marginals[i] * maxExpected) + ((1.0 - marginals[i]) * minExpected))))

        maxExpected, minExpected = -1, -1
        modelBase += 16

    return EVPIs, scenarios