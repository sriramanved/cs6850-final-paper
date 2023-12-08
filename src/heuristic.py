import sys
sys.path.append('../models')

import circuit
import grid
import random
import matplotlib.pyplot as plt
import numpy as np


#################################### parameters ################################

# recovery times for UAVs launch and rendezvous
sL = 0
sR = 0

# UAV eligible customers

# generate random eligible customers from range 1 - 2500
# cPrime = random.sample(range(1, 625), 200)
cPrime = [2, 3, 6]

# drones available
# num_drones = 20
num_drones = 3

# battery budget for all drones
B = 10000

# energy budget for each drone
energy = [B for _ in range(num_drones)]

################################### initialization #############################

# solve TSP
truckRoute, t = circuit.solveTSP()

# initialize savings & maxSavings
savings = 0
maxSavings = 0

# servedByUAV[i] = d if customer node i is served by drone d, -1 if served by truck
servedByUAV = [-1 for _ in range(len(truckRoute))]
iStar, jStar, kStar = -1, -1, -1


# tau is the distance matrix
tau = (circuit.create_data_model())["distance_matrix"]

# tau_prime+/- [0, 10] randomly for each tau[i][j] to construct matrix tau_prime, but use the same seed every time. All values in tau_prime are positive.
random.seed(0)
tau_prime = tau.copy()
for i in range(len(tau)):
    for j in range(len(tau[i])):
        tau_prime[i][j] = abs(tau[i][j] - random.randint(0, 10)) if tau[i][j] != 0 else 0

# initialize the sorties dictionary: sorties[d][j] = (i, k) if drone d serves customer node j between node i and node k
sorties = dict([i, {}] for i in range(num_drones))

# availableUAVs[i] = [d1, d2, ...] if node i is available to drones d1, d2, ...
availableUAVs = {}
for i in range(len(truckRoute)):
    availableUAVs[i] = list(range(num_drones))

# unavailableUAVs[i] = [d1, d2, ...] if node i is unavailable to drones d1, d2, ...
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
        # print("available at this time ", 0 in availableUAVs[141])
        for j in cPrime:
            calcSavings(j, t)
            # no available UAV or j is beginning/ end of sortie
            if len(availableUAVs[j]) == 0:
                calcCostTruck(j, t)
            else:
                calcCostUAV(j, t)

        # print("available at this time ", 0 in availableUAVs[141])
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
    iIdx = jIdx - 1 # we need to test whether iIdx out of bounds.
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
        # if d == 0:
            # print("start, end", start, end)
            # print("at start and at end", truckRoute[start], truckRoute[end])
            # print("jIdx: ", jIdx, j)
        for iIdx in range(start, end + 1): # removed end + 1 because i != k for insertions
            i = truckRoute[iIdx]
            for kIdx in range(iIdx + 1, end + 1):
                k = truckRoute[kIdx]
                if tau_prime[i][j] + tau_prime[j][k] <= energy[d]:
                    cost = tau[i][j] + tau[j][k] - tau[i][k]
                    if savings - cost > maxSavings and i != j and j != k:
                        # if d == 0:
                        #     print("setting j*")
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

    # print("truck route: ", truckRoute)

    # print("\nsorties: ", sorties)

    # print("available at this time 1", 0 in availableUAVs[141])

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

        # print("available at this time 2", 0 in availableUAVs[141])
        # update unavailableUAVs and availableUAVs
        # print("jStar: ", jStar)
        # print("iIdx: ", iIdx)
        # print("kIdx: ", kIdx)
        # print("curr drone: ", curr_d)
        for x in range(iIdx + 1, kIdx):
            # print("available here:", availableUAVs[truckRoute[x]])
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
        iIdx = truckRoute.index(iStar)
        jIdx = truckRoute.index(jStar)
        kIdx = truckRoute.index(kStar)

        truckRoute.remove(jStar)
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
    solveFSTSP(cPrime)

    print("Truck Route: ", truckRoute)
    print("Sorties: ", sorties)

    # print("Grid model chosen for this run: ", "grid")
    # print("cPrime generated randomly: 200 customers [1, 625]]")
    print("Number of drones: ", num_drones)
    print("Battery budget: ", B)




if __name__ == "__main__":
    main()
################################# HELPER FUNCTIONS #############################