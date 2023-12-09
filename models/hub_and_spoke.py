"""Simple Travelling Salesperson Problem (TSP) between cities."""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math


def create_hub_spoke_distance_matrix(levels, c1, c2, r):
    # Calculate the number of nodes: 1 hub + 8 spokes per level
    num_nodes = 1 + levels * 8
    # Initialize the distance matrix with zeros
    distance_matrix = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]

    # Fill in the distances for the hub (node 0) to all other nodes
    for i in range(1, num_nodes):
        distance_matrix[0][i] = distance_matrix[i][0] = c1 * ((i - 1) // 8 + 1)

    # Fill in the distances for all other nodes
    for i in range(1, num_nodes):
        for j in range(i + 1, num_nodes):
            level_i = (i - 1) // 8
            level_j = (j - 1) // 8
            pos_i = (i - 1) % 8
            pos_j = (j - 1) % 8

            if level_i == level_j:
                # Nodes are on the same level, use circumference distance
                distance_matrix[i][j] = distance_matrix[j][i] = min(abs(pos_i - pos_j), 8 - abs(pos_i - pos_j)) * (c2 + level_i * r)
            else:
                # Nodes are on different levels, calculate the Manhattan-like distance
                radial_distance = c1 * abs(level_i - level_j)
                # Choose the shorter path around the octagon, either clockwise or counter-clockwise
                circum_distance = min(abs(pos_i - pos_j), 8 - abs(pos_i - pos_j)) * (c2 + max(level_i, level_j) * r)
                distance_matrix[i][j] = distance_matrix[j][i] = radial_distance + circum_distance

    return distance_matrix

def create_euclidean_hub_spoke_distance_matrix(levels, c1, c2, r):
    # Calculate the number of nodes: 1 hub + 8 spokes per level
    num_nodes = 1 + levels * 8
    # Initialize the Euclidean distance matrix with zeros
    euclidean_distance_matrix = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]

    # Calculate the positions of each node in Cartesian coordinates
    positions = [(0, 0)]  # Starting with the hub at the origin
    for level in range(1, levels + 1):
        radius = c1 * level
        for i in range(8):
            angle = math.pi / 4 * i
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions.append((x, y))

    # Calculate Euclidean distances
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                xi, yi = positions[i]
                xj, yj = positions[j]
                euclidean_distance_matrix[i][j] = math.hypot(xj - xi, yj - yi)
            else:
                euclidean_distance_matrix[i][j] = 0

    return euclidean_distance_matrix


def create_data_model():
    """Stores the data for the problem."""
    data = {}

    levels = 3  # 3 concentric octagons
    c1 = 1  # Radial distance constant
    c2 = 1  # Initial circumference distance
    r = 0.5  # Rate of increase per level

    # Create Manhattan distance matrix
    data["distance_matrix"] = create_hub_spoke_distance_matrix(levels, c1, c2, r)

    # Create Euclidean distance matrix
    data["euclidean_distance_matrix"] = create_euclidean_hub_spoke_distance_matrix(levels, c1, c2, r)

    data["num_vehicles"] = 1
    data["depot"] = 0

    return data


def print_solution(manager, routing, solution):
    t = [0]
    route = [0]
    """Prints solution on console."""
    # print(f"Objective: {solution.ObjectiveValue()} miles")
    index = routing.Start(0)
    plan_output = "Route for vehicle 0:\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += f" {manager.IndexToNode(index)} ->"
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(
            previous_index, index, 0)
        route.append(manager.IndexToNode(index))
        t += [route_distance]
    plan_output += f" {manager.IndexToNode(index)}\n"

    # print(plan_output)
    plan_output += f"Route distance: {route_distance}miles\n"
    return route, t


def solveTSP():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        route, t = print_solution(manager, routing, solution)
    return route, t


def main():
    route, t = solveTSP()
    print(route)
    print(t)

if __name__ == "__main__":
    main()
