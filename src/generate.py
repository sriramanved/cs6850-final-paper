import requests
import json
import math
import random

cities = [
    "Ithaca NY",
    "Albany NY",
    "New Haven CT",
    "Hartford CT",
    "Boston MA",
    "Concord NH",
    "Portland ME",
    "Utica NY",
    "Philadelphia PA",
    "Newark NJ",
    "New York City NY",
    "Harrisburg PA",
    "Pittsburgh PA",
    "Annapolis MD",
    "Dover DE",
    "Arlington VA",
    "Richmond VA",
    "Columbus OH",
    "Cincinnati OH",
    "Charleston WV",
    "Lexington KY",
    "Charlotte NC",
    "Nashville TN"
]


# Function to divide a list into chunks of specified size.
def chunk_list(input_list, chunk_size):
    """Divide a list into chunks of specified size."""
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i : i + chunk_size]


# Split the list of cities into chunks of 10
city_chunks = list(chunk_list(cities, 10))


# Function to make API request.
def make_api_request(origins, destinations):
    params = {
        "origins": "|".join(origins),
        "destinations": "|".join(destinations),
        "mode": "driving",
        "units": "imperial",
        "language": "en-US",
        "key": "AIzaSyDZkzMKatrMp8n2XNQPtC5tdIAOa9l_zSo",
    }
    response = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json", params=params
    )
    return response.json()


# Making requests for each combination of chunks and updating the distance matrix. Instead of making API requests for every pair, we make requests only for unique combinations. After each request, we update two positions in the matrix - one for the origin-to-destination distance, and one for the destination-to-origin distance.
def make_distance_matrix(tri_state_area_cities):
    distance_matrix = [
        [0 if i == j else None for j in range(len(tri_state_area_cities))]
        for i in range(len(tri_state_area_cities))
    ]
    city_chunks = list(chunk_list(tri_state_area_cities, 10))
    for i, chunk1 in enumerate(city_chunks):
        for j, chunk2 in enumerate(city_chunks):
            if j >= i:  # Ensure we're not repeating the same pair
                data = make_api_request(chunk1, chunk2)
                if data["status"] == "OK":
                    for x, origin in enumerate(chunk1):
                        for y, destination in enumerate(chunk2):
                            element = data["rows"][x]["elements"][y]
                            if element["status"] == "OK":
                                distance = element.get("distance")
                                if distance:
                                    # Convert meters to miles
                                    distance_value = int(
                                        math.ceil(distance["value"] / 1609.34)
                                    )
                                    origin_index = tri_state_area_cities.index(origin)
                                    destination_index = tri_state_area_cities.index(
                                        destination
                                    )
                                    distance_matrix[origin_index][
                                        destination_index
                                    ] = distance_value
                                    # Reflect across diagonal
                                    distance_matrix[destination_index][
                                        origin_index
                                    ] = distance_value
                                else:
                                    print(
                                        f"No road route between {origin} and {destination}"
                                    )
                            else:
                                print(f"API call failed for {origin} to {destination}")
    return distance_matrix


# Aggregates all distance matrices together
def compute_all():
    all_distance_matrices = []

    length_of_cities = len(cities)

    number_of_iterations = 20
    cities_to_add_each_time = 1

    for i in range(number_of_iterations):
        number_of_cities = cities_to_add_each_time * (i + 1)
        sampled_cities = random.sample(cities, min(number_of_cities, length_of_cities))
        distance_matrix = make_distance_matrix(sampled_cities)
        all_distance_matrices.append(distance_matrix)

    return all_distance_matrices


def compute_3():
    small = make_distance_matrix(cities[:8])
    medium = make_distance_matrix(cities[:14])
    large = make_distance_matrix(cities[:20])
    return small, medium, large


# Print the distance matrix
def print_matrix(matrix):
    for row in matrix:
        print(row)
