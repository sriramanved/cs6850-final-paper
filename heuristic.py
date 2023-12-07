import circuit

cPrime = []  # UAVs
truckRoute, t = circuit.solveTSP()
savings = 0
maxSavings = 0
num_drones = 10  # drones available
servedByUAV = []

available = {}
for i in range(len(cPrime)):
    available[i] = [range(len(num_drones))]
    

def solveFTSTP(circuit, Cprime, UAVs, customers, max_iter=1000):
    while iter < max_iter:
        for j in Cprime:
            calcSavings(j, t)
            # no available UAV or j is beginning/ end of sortie
            if len(available[j]) == 0 or sortiePart(j):
                calcCostTruck(j, t)
            else:
                calcCostUAV(j, t)

        if maxSavings > 0:
            performUpdate()
            maxSavings = 0
        else:
            break
        iter += 1
    return

def calcSavings(j, t):
    return

def calcCostTruck(j, t):
    return

def calcCostUAV(j, t):
    return


def performUpdate():
    return
	
################################# HELPER FUNCTIONS #############################


def sortiePart(j):
    return True