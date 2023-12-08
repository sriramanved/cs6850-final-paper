import circuit
import random

#################################### parameters ################################

# recovery times for UAVs launch and rendezvous
sL = 0
sR = 0

# UAV eligible customers
cPrime = [2, 3, 6]

# drones available
num_drones = 3

# battery budget for all drones
B = 100

# energy budget for each drone
energy = [B for _ in range(num_drones)]

################################### initialization #############################

# solve TSP
truckRoute, t = circuit.solveTSP()

# map every customer in the truck route to its index in the truck route
truckRouteMap = {}
for i in range(len(truckRoute)):
    truckRouteMap[truckRoute[i]] = i

# initialize savings & maxSavings
savings = 0
maxSavings = 0

# servedByUAV[i] = d if customer node i is served by drone d, -1 if served by truck
servedByUAV = [-1 for _ in range(len(truckRoute))]
iStar, jStar, kStar = -1, -1, -1


# tau is the distance matrix
tau = (circuit.create_data_model())["distance_matrix"]

# tau_prime+/- [0, 10] randomly for each tau[i][j] to construct matrix tau_prime, but use the same seed every time.
random.seed(0)
tau_prime = tau.copy()
for i in range(len(tau)):
    for j in range(len(tau[i])):
        tau_prime[i][j] = tau[i][j] + \
            random.randint(0, 10) * random.choice([-1, 1])

# initialize the sorties dictionary: sorties[d][j] = (i, k) if drone d serves customer node j between index i and index k
sorties = dict([i, {}] for i in range(num_drones))

# availableUAVs[i] = [d1, d2, ...] if node i is available to drones d1, d2, ...
availableUAVs = {}
for i in range(len(truckRoute)):
    availableUAVs[i] = list(range(num_drones))

# unavailableUAVs[i] = [d1, d2, ...] if node i is unavailable to drones d1, d2, ...
unavailableUAVs = {}
for i in range(len(truckRoute)):
    unavailableUAVs[i] = []
print("Unavailable UAVs", unavailableUAVs)


def solveFSTSP(cPrime, max_iter=1000):
    """
    Main Heuristic method. 
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, t, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, truckRouteMap

    iter = 0
    while iter < max_iter:
        print("ITERATION:", iter)
        for j in cPrime:
            calcSavings(j, t)
            # no available UAV or j is beginning/ end of sortie
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
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, truckRouteMap

    jIdx = truckRouteMap[j]
    iIdx = jIdx - 1
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
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, truckRouteMap

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
    """
    global maxSavings, iStar, jStar, kStar, savings, tau, tau_prime, truckRoute, sorties, availableUAVs, unavailableUAVs, energy, servedByUAV, truckRouteMap

    D = availableUAVs[j]
    jIdx = truckRouteMap[j]
    for d in D:
        a = -1
        b = len(truckRoute) + 2
        print("d: ", d)
        jdict = sorties[d]
        # l and rv are indicies in truck route
        print("jdict", jdict)
        for (l, rv) in jdict.values():
            a = rv if rv < jIdx and rv > a else a
            b = l if l > jIdx and l < b else b
        for iIdx in range(max(a, 0), min(b, len(truckRoute))):
            i = truckRoute[iIdx]
            for kIdx in range(iIdx + 1, min(b + 1, len(truckRoute))):
                k = truckRoute[kIdx]
                if tau_prime[i][j] + tau_prime[j][k] <= energy[d]:
                    cost = tau[i][j] + tau[j][k] - tau[i][k]
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

    print("vals of i*, j*, k*", iStar, jStar, kStar)
    print("truckRoute before: ", truckRoute)

    if servedByUAV[jStar] != -1:
        iIdx = truckRouteMap[iStar]
        jIdx = truckRouteMap[jStar]
        kIdx = truckRouteMap[kStar]
        # what truck services before and after jIdx
        iPrime = truckRoute[jIdx - 1]
        kPrime = truckRoute[jIdx + 1]
        truckSavings = tau[iPrime][jStar] + \
            tau[jStar][kPrime] - tau[iPrime][kPrime]

        curr_d = servedByUAV[jStar]

        energy[curr_d] -= (t[kIdx] - t[iIdx])

        # update unavailableUAVs and availableUAVs
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
        print("jStar: ", jStar)

        # update truckRoute map
        truckRouteMap[jStar] = -1
        for x in range(jIdx, len(truckRoute)):
            truckRouteMap[truckRoute[x]] -= 1

        # update sorties
        sorties[curr_d][jStar] = (iStar, kStar)
    else:
        # update truckRoute
        iIdx = truckRoute[iStar]
        jIdx = truckRoute[jStar]
        kIdx = truckRoute[kStar]

        truckRoute.remove(jStar)
        truckRoute.insert(jStar, iIdx + 1)

        # update truckRoute map
        for x in range(jIdx + 1, len(truckRoute)):
            truckRouteMap[truckRoute[x]] -= 1

        truckRouteMap[jStar] = iIdx + 1
        for x in range(kIdx, len(truckRoute)):
            truckRouteMap[truckRoute[x]] += 1

        # update unavailable, available uavs
        unavailableUAVs[jStar] = list(
            set(unavailableUAVs[iStar] + unavailableUAVs[kStar]))
        availableUAVs[jStar] = list(
            set(availableUAVs[iStar]).intersection(set(availableUAVs[kStar])))

        for d in unavailableUAVs[jStar]:
            energy[d] -= tau[iStar][jStar] + tau[jStar][kStar]

        for x in range(jIdx + 1, len(truckRoute)):
            t[x] += truckSavings
    print("truckRoute after: ", truckRoute)
    print("sorties after: ", sorties)


def main():
    """
    Main method for heuristic.
    """
    solveFSTSP(cPrime)

    print("Truck Route: ", truckRoute)
    print("Sorties: ", sorties)


if __name__ == "__main__":
    main()
################################# HELPER FUNCTIONS #############################
