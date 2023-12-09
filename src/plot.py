import sys

sys.path.append("../models")

import solve_matrix
import heuristic
import generate as gen
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

matrices = gen.compute_all()

num_drones = 3
B = 1000
sL = 0
sR = 0

t_array = []
size = []

for distance_matrix in matrices:
    truckRoute, t = solve_matrix.solveTSP(distance_matrix)
    truckRoute[-1] = len(truckRoute) - 1

    # tau is the distance matrix for truck and tau_prime is for drone
    data = solve_matrix.create_data_model(distance_matrix)

    # cPrime should choose a proportion of the total number of customers and then pick that many random customers
    num_of_customers = int(len(distance_matrix) * 0.4)
    cPrime = np.random.choice(
        len(distance_matrix) - 1, num_of_customers, replace=False
    ) + 1
    cPrime = cPrime.tolist()

    tau = np.array(data["distance_matrix"])
    tau = np.vstack([tau, tau[0, :]])
    tau = np.hstack([tau, tau[:, 0].reshape(-1, 1)])
    data["distance_matrix"] = tau.tolist()

    tau_prime = np.array(data["tau_prime"])
    tau_prime = np.vstack([tau_prime, tau_prime[0, :]])
    tau_prime = np.hstack([tau_prime, tau_prime[:, 0].reshape(-1, 1)])
    data["tau_prime"] = tau_prime.tolist()

    truckRoute, sorties, t = heuristic.solveMFSHC(
        num_drones, B, truckRoute, t, data, cPrime, sL, sR
    )
    
    size.append(len(distance_matrix))
    t_array.append(t[-1])

sns.set_theme(style="darkgrid")
sns.set_palette("husl")
plt.scatter(size, t_array)
plt.xlabel("Number of Customers")
plt.ylabel("Total Delivery Time")
plt.title("Total Delivery Time vs Number of Customers")

#line of best fit
z = np.polyfit(size, t_array, 1)
p = np.poly1d(z)
plt.plot(size,p(size),"r--")

plt.show()

# num drones vs total delivery time on 3 diff grid sizes


# time saved for fixed number of drones for diff grid sizes
