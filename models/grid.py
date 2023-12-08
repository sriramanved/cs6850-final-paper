"""Simple Travelling Salesperson Problem (TSP) between cities."""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_distance_matrix(grid_size):
    n = grid_size * grid_size
    distance_matrix = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(grid_size):
        for j in range(grid_size):
            point1 = i * grid_size + j

            for x in range(grid_size):
                for y in range(grid_size):
                    point2 = x * grid_size + y
                    distance = abs(x - i) + abs(y - j)
                    distance_matrix[point1][point2] = distance

    return distance_matrix


def create_data_model():
    """Stores the data for the problem."""
    data = {}

    # Create distance matrix
    data["distance_matrix"] = create_distance_matrix(25)

    data["num_vehicles"] = 1
    data["depot"] = 0
    # for i in range(len(data["distance_matrix"])):
    #     print(data["distance_matrix"][i])
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
    # print(route)
    # print(t)


if __name__ == "__main__":
    main()
