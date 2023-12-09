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
import sys
sys.path.append('../models')


def solveMFSHC(num_drones, B, truckRoute, t, data, cPrime, sL, sR):
    """
    solve method for heuristic.
    """

    ############################## parameters ##############################

    # energy budget for each drone
    energy = [B for _ in range(num_drones)]

    # tau is the distance matrix
    tau = data["distance_matrix"]

    # tau_prime is the distance matrix for drones
    tau_prime = data["tau_prime"]

    # initialize savings & maxSavings
    savings = 0
    maxSavings = 0

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

    print("Time with just truck: ", t[-1] / 50)
    print("Truck route before: ", truckRoute)
    truckRoute, sorties, t = solveFSTSP(
        cPrime, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, sL, sR)

    print("Truck Route: ", truckRoute)
    print("Sorties: ", sorties)
    print("Total time in hours: ", t[-1] / 50)

    print("Number of drones: ", num_drones)
    print("Battery budget: ", B)
    print("=====================================")
    return truckRoute, sorties, t


def solveFSTSP(cPrime, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, sL, sR, max_iter=500):
    """
    Main Heuristic method. 
    """

    iter = 0
    while iter < max_iter:
        print("WORKING AT ITERATION:", iter)

        for j in cPrime:
            t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV = calcSavings(
                j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV)
            print("j, savings: ", j, savings)
            # no available UAV or j is beginning/ end of sortie
            if len(availableUAVs[j]) == 0:
                t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV = calcCostTruck(
                    j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV)
            else:
                t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV = calcCostUAV(
                    j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, sL, sR)
            print("maxSavings: ", maxSavings)
        if maxSavings > 0:
            maxSavings, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV = performUpdate(
                cPrime, iStar, jStar, kStar, maxSavings, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV)
            maxSavings = 0
        else:
            break
        iter += 1
    return truckRoute, sorties, t


def calcSavings(j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV):
    """
    Minimizes the difference between the drone and the truck arrivals at a single location. The simplifcation of our actual pseudocode is that we assume that the drone never has to wait for the truck to arrive at a location.
    """

    jIdx = truckRoute.index(j)
    iIdx = jIdx - 1  # we need to test whether iIdx out of bounds.
    kIdx = jIdx + 1
    i = truckRoute[iIdx]
    k = truckRoute[kIdx]

    savings = tau[i][j] + tau[j][k] - tau[i][k]
    # calculate a, b, j' and update savings.
    return t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV


def calcCostTruck(j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV):
    """
    Computes the time saved by inserting j at different positions of the route. We assume that node j is initially being served by the truck.
    @param j: node to be inserted
    @param t: time of arrival at each node in the truck route
    """

    for iIdx in range(len(truckRoute) - 1):
        kIdx = iIdx + 1
        i = truckRoute[iIdx]
        k = truckRoute[kIdx]
        cost = tau[i][j] + tau[j][k] - tau[i][k]
        # print("truck cost:", cost)
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
    return t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV


def calcCostUAV(j, t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, sL, sR):
    """
    Computes the time saved by assigning an available UAV to a node j that initially recieved tis delivery by truck.
    @param j: node to be inserted
    @param t: time of arrival at each node in the truck route
    """

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
        print("b, len(truckRoute) - 1: ", b)
        print("drone, start, end: ", d, start, end)
        for iIdx in range(start, end + 1):
            i = truckRoute[iIdx]
            for kIdx in range(iIdx + 1, end + 1):
                k = truckRoute[kIdx]
                if tau_prime[i][j] + tau_prime[j][k] <= energy[d]:
                    cost = tau[i][j] + tau[j][k] - tau[i][k] + sL + sR
                    print("cost, i, j, k: ", cost, i, j, k)
                    if savings - cost > maxSavings and i != j and j != k:
                        servedByUAV[j] = d
                        iStar = i
                        jStar = j
                        kStar = k

                        maxSavings = savings - cost
    return t, maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV


def performUpdate(cPrime, iStar, jStar, kStar, maxSavings, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV):
    """
    Performs the update of the truck route and the UAV sorties.
    """

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
    return maxSavings, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV


def main():
    """
    Main method.
    """

    # generate data
    data = cities.create_data_model()
    # data = grid.generate_data(200, 625)
    # data = rural.generate_data(200, 625)

    # get the truck route
    truckRoute, t = cities.solveTSP()

    # get the cPrime set
    cPrime = [2, 3, 6]

    # get the number of drones
    num_drones = 3

    sL = 0
    sR = 0
    # get the battery budget
    B = float("inf")

    # solve the MFSHC problem
    solveMFSHC(num_drones, B, truckRoute, t, data, cPrime, sL, sR)


if __name__ == "__main__":
    main()
