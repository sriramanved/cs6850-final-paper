import sys
sys.path.append('../models')

import cities
import matplotlib.pyplot as plt
import math
import random
import circuit
import seaborn as sns
import numpy as np
import grid
import rural


import hub_and_spoke
#################################### parameters ################################

# recovery times for UAVs launch and rendezvous
sL = 0
sR = 0

# drones available
# num_drones = 20
num_drones = 5

# battery budget for all drones
B = float("inf")

# energy budget for each drone
energy = [B for _ in range(num_drones)]

################################### initialization #############################

# solve TSP using OR-Tools
truckRoute, t = grid.solveTSP()

# tau is the distance matrix for truck and tau_prime is for drone
data = grid.create_data_model()

# tau is the distance matrix
tau = data["distance_matrix"]

# tau_prime is the distance matrix for drones
tau_prime = data["tau_prime"]

# initialize savings & maxSavings
savings = 0
maxSavings = 0

# cPrime = random.sample(range(1, len(truckRoute)), 50)
cPrime = [2, 3, 6, 7]

# servedByUAV[i] = d if customer node i is served by drone d, -1 if served by truck
servedByUAV = [-1 for _ in range(len(truckRoute))]
iStar, jStar, kStar = -1, -1, -1

# initialize the sorties dictionary: sorties[d][j] = (i, k) if drone d serves customer node j between node i and node k
sorties = dict([i, {}] for i in range(num_drones))

# availableUAVs[i] = [d1, d2, ...] if node i is available to the set of drones {d1, d2, ...}
availableUAVs = {}
for i in range(len(truckRoute)):
    availableUAVs[i] = list(range(num_drones))

# unavailableUAVs[i] = [d1, d2, ...] if node i is unavailable to the set of drones {d1, d2, ...}
unavailableUAVs = {}
for i in range(len(truckRoute)):
    unavailableUAVs[i] = []


def solveFSTSP(cPrime, max_iter=500):
    """
    Main Heuristic method. 
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV

    iter = 0
    while iter < max_iter:
        print("WORKING AT ITERATION:", iter)

        for j in cPrime:
            calcSavings(j, t)
            if len(availableUAVs[j]) == 0:
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
    """
    Minimizes the difference between the drone and the truck arrivals at a single location. The simplifcation of our actual pseudocode is that we assume that the drone never has to wait for the truck to arrive at a location.
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV

    jIdx = truckRoute.index(j)
    iIdx = jIdx - 1  # we need to test whether iIdx out of bounds.
    kIdx = jIdx + 1
    i = truckRoute[iIdx]
    k = truckRoute[kIdx]
    savings = tau[i][j] + tau[j][k] - tau[i][k]
    # calculate a, b, j' and update savings.
    return savings


def calcCostTruck(j, t):
    """
    Computes the time saved by inserting j at different positions of the route. We assume that node j is initially being served by the truck.
    @param j: node to be inserted
    @param t: time of arrival at each node in the truck route
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV

    for iIdx in range(len(truckRoute) - 1):
        kIdx = iIdx + 1
        i = truckRoute[iIdx]
        k = truckRoute[kIdx]
        cost = tau[i][j] + tau[j][k] - tau[i][k]
        if cost < savings:
            feasible = True
            for d in set(unavailableUAVs[i] + unavailableUAVs[k]):
                feasible = feasible and energy[d] - \
                    cost > 0 and savings - cost <= maxSavings
            if feasible:
                servedByUAV[j] = -1
                iStar = i
                jStar = j
                kStar = k
                maxSavings = savings - cost


def calcCostUAV(j, t):
    """
    Computes the time saved by assigning an available UAV to a node j that initially recieved tis delivery by truck.
    @param j: node to be inserted
    @param t: time of arrival at each node in the truck route
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV

    D = availableUAVs[j]
    jIdx = truckRoute.index(j)
    for d in D:
        a = -1
        b = len(truckRoute) + 2
        jdict = sorties[d]
        for (l, rv) in jdict.values():
            lIdx = truckRoute.index(l)
            rvIdx = truckRoute.index(rv)
            a = rvIdx if rvIdx < jIdx and rvIdx > a else a
            b = lIdx if lIdx > jIdx and lIdx < b else b
        start = max(a, 0)
        end = min(b, len(truckRoute) - 1)
        for iIdx in range(start, end + 1):
            i = truckRoute[iIdx]
            for kIdx in range(iIdx + 1, end + 1):
                k = truckRoute[kIdx]
                if tau_prime[i][j] + tau_prime[j][k] <= energy[d]:
                    cost = tau[i][j] + tau[j][k] - tau[i][k] + sL + sR
                    if savings - cost > maxSavings and i != j and j != k:
                        servedByUAV[j] = d
                        iStar = i
                        jStar = j
                        kStar = k
                        maxSavings = savings - cost


def performUpdate():
    """
    Performs the update of the truck route and the UAV sorties.
    """
    global iStar, jStar, kStar, maxSavings, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV

    if servedByUAV[jStar] != -1:
        iIdx = truckRoute.index(iStar)
        jIdx = truckRoute.index(jStar)
        kIdx = truckRoute.index(kStar)
        # what truck services before and after jIdx
        iPrime = truckRoute[jIdx - 1]
        kPrime = truckRoute[jIdx + 1]
        truckSavings = tau[iPrime][jStar] + \
            tau[jStar][kPrime] - tau[iPrime][kPrime]

        curr_d = servedByUAV[jStar]

        energy[curr_d] -= (t[kIdx] - t[iIdx])

        for x in range(iIdx + 1, kIdx):
            availableUAVs[truckRoute[x]].remove(curr_d)
            unavailableUAVs[truckRoute[x]].append(curr_d)

        for d in unavailableUAVs[jStar]:
            energy[d] += truckSavings

        if iStar in cPrime:
            cPrime.remove(iStar)
        cPrime.remove(jStar)
        if kStar in cPrime:
            cPrime.remove(kStar)

        # update t
        for x in range(jIdx + 1, len(truckRoute)):
            t[x] -= truckSavings

        # update truckRoute
        truckRoute.remove(jStar)

        # update sorties
        sorties[curr_d][jStar] = (iStar, kStar)
    else:
        truckSavings = tau[iStar][jStar] + \
            tau[jStar][kStar] - tau[iStar][kStar]

        # update truckRoute
        truckRoute.remove(jStar)

        iIdx = truckRoute.index(iStar)
        jIdx = truckRoute.index(jStar)
        kIdx = truckRoute.index(kStar)

        truckRoute.insert(iIdx + 1, jStar)

        # update unavailable, available uavs
        unavailableUAVs[jStar] = list(
            set(unavailableUAVs[iStar] + unavailableUAVs[kStar]))
        availableUAVs[jStar] = list(
            set(availableUAVs[iStar]).intersection(set(availableUAVs[kStar])))

        # update drone energies
        for d in unavailableUAVs[jStar]:
            energy[d] -= tau[iStar][jStar] + tau[jStar][kStar]

        # displace all arrival times after the insertion of jStar into truckRoute
        for x in range(jIdx + 1, len(truckRoute)):
            t[x] += truckSavings
    
    
def main():
    """
    Main method for heuristic.
    """
    print("Time with just truck: ", t[-1] / 50)
    print("Truck route before: ", truckRoute)
    solveFSTSP(cPrime)

    print("Truck Route: ", truckRoute)
    print("Sorties: ", sorties)
    print("Total time in hours: ", t[-1] / 50)

    print("Number of drones: ", num_drones)
    print("Battery budget: ", B)


if __name__ == "__main__":
    main()
################################# HELPER FUNCTIONS #############################
