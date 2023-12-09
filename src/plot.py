import sys
sys.path.append('../models')

import solve_matrix
import heuristic
import generate as gen
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

matrices = gen.compute_all()

num_drones = 3
B = 10000
sL = 0
sR = 0

t_array = []
size = []

for distance_matrix in matrices:

    truckRoute, t = solve_matrix.solveTSP(distance_matrix)

    # tau is the distance matrix for truck and tau_prime is for drone
    data = solve_matrix.create_data_model(distance_matrix)

    # cPrime should choose a proportion of the total number of customers and then pick that many random customers
    num_of_customers = int(len(distance_matrix) * 1)
    cPrime = np.random.choice(len(distance_matrix),
                              num_of_customers, replace=False).tolist()
    truckRoute, sorties, t = heuristic.solveMFSHC(
        num_drones, B, truckRoute, t, data, cPrime, sL, sR)
    # size.append(len(distance_matrix))
    # t_array.append(t[-1])

# plot
# sns.set_theme(style="darkgrid")
# sns.set_palette("husl")
# plt.plot(size, t_array)
# plt.xlabel("Number of Customers")
# plt.ylabel("Total Delivery Time")
# plt.title("Total Delivery Time vs Number of Customers")
# plt.show()

# num drones vs total delivery time on 3 diff grid sizes


# time saved for fixed number of drones for diff grid sizes
