import sys

sys.path.append("../models")

import solve_matrix
import heuristic
import generate as gen
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

small, medium, large = gen.compute_3()

num_drones = 3
B = 100
sL = 0
sR = 0

np.random.seed(6850)

t_array_small = []
t_array_medium = []
t_array_large = []
num_drones = list(range(1, 11))

for i in num_drones:
    small_cPrime = (np.random.choice(range(1, len(small)), 2, replace=False)).tolist()
    truckRoute, t = solve_matrix.solveTSP(small)
    truckRoute[-1] = len(truckRoute) - 1

    data = solve_matrix.create_data_model(small)

    tau = np.array(data["distance_matrix"])
    tau = np.vstack([tau, tau[0, :]])
    tau = np.hstack([tau, tau[:, 0].reshape(-1, 1)])
    data["distance_matrix"] = tau.tolist()

    tau_prime = np.array(data["tau_prime"])
    tau_prime = np.vstack([tau_prime, tau_prime[0, :]])
    tau_prime = np.hstack([tau_prime, tau_prime[:, 0].reshape(-1, 1)])
    data["tau_prime"] = tau_prime.tolist()

    truckRoute, sorties, t = heuristic.solveMFSHC(
        i, B, truckRoute, t, data, small_cPrime, sL, sR
    )

    t_array_small.append(t[-1])


for i in num_drones:
    medium_cPrime = (np.random.choice(range(1, len(medium)), 4, replace=False)).tolist()
    truckRoute, t = solve_matrix.solveTSP(medium)
    truckRoute[-1] = len(truckRoute) - 1

    data = solve_matrix.create_data_model(medium)

    tau = np.array(data["distance_matrix"])
    tau = np.vstack([tau, tau[0, :]])
    tau = np.hstack([tau, tau[:, 0].reshape(-1, 1)])
    data["distance_matrix"] = tau.tolist()

    tau_prime = np.array(data["tau_prime"])
    tau_prime = np.vstack([tau_prime, tau_prime[0, :]])
    tau_prime = np.hstack([tau_prime, tau_prime[:, 0].reshape(-1, 1)])
    data["tau_prime"] = tau_prime.tolist()

    truckRoute, sorties, t = heuristic.solveMFSHC(
        i, B, truckRoute, t, data, medium_cPrime, sL, sR
    )

    t_array_medium.append(t[-1])


for i in num_drones:
    large_cPrime = (np.random.choice(range(1, len(large)), 7, replace=False)).tolist()
    truckRoute, t = solve_matrix.solveTSP(large)
    truckRoute[-1] = len(truckRoute) - 1

    data = solve_matrix.create_data_model(large)

    tau = np.array(data["distance_matrix"])
    tau = np.vstack([tau, tau[0, :]])
    tau = np.hstack([tau, tau[:, 0].reshape(-1, 1)])
    data["distance_matrix"] = tau.tolist()

    tau_prime = np.array(data["tau_prime"])
    tau_prime = np.vstack([tau_prime, tau_prime[0, :]])
    tau_prime = np.hstack([tau_prime, tau_prime[:, 0].reshape(-1, 1)])
    data["tau_prime"] = tau_prime.tolist()

    truckRoute, sorties, t = heuristic.solveMFSHC(
        i, B, truckRoute, t, data, large_cPrime, sL, sR
    )

    t_array_large.append(t[-1])

sns.set_theme(style="darkgrid")
sns.set_palette("husl")
plt.plot(num_drones, t_array_small, label="Small")
plt.plot(num_drones, t_array_medium, label="Medium")
plt.plot(num_drones, t_array_large, label="Large")
plt.xlabel("Number of Drones")
plt.ylabel("Total Delivery Time")
plt.title("Total Delivery Time vs Number of Drones")
plt.legend()
plt.show()
# num drones vs total delivery time on 3 diff grid sizes


# time saved for fixed number of drones for diff grid sizes
