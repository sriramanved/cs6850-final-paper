"""Simple Travelling Salesperson Problem (TSP) between cities."""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import math


def txt_to_distance_matrix(txt):
    """
    txt: txt file with distance matrix
    return: distance matrix
    """
    path = "../data/"
    with open(path + txt, "r") as f:
        lines = f.readlines()
    distance_matrix = []
    for line in lines:
        distance_matrix.append([int(math.ceil(float(i)*10))
                               for i in line.split(",")])
    return distance_matrix


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = txt_to_distance_matrix("tau.txt")
    data["num_vehicles"] = 1
    data["depot"] = 0
    data["tau_prime"] = txt_to_distance_matrix("tau_prime.txt")
    print(data["distance_matrix"])
    return data


def print_solution(manager, routing, solution):
    t = [0]
    route = [0]
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()} miles")
    index = routing.Start(0)
    plan_output = "Route for vehicle 0:\n"
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += f" {manager.IndexToNode(index)} ->"
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(
            previous_index, index, 0)
        print("prev index: ", previous_index)
        print("index: ", index)
        route.append(manager.IndexToNode(index))
        t += [route_distance]
    plan_output += f" {manager.IndexToNode(index)}\n"

    print(plan_output)
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
