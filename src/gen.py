import requests
import json
import math

all_distance_matrices = []

tri_state_area_cities = ["New York City NY", "Philadelphia PA", "Stamford CT", "Ithaca NY", "Newark NJ", "Jersey City NJ", "New Brunswick NJ", "Hoboken NJ", "Princeton NJ", "Trenton NJ", "Yonkers NY"]

def chunk_list(input_list, chunk_size):
    """Divide a list into chunks of specified size."""
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]

# Initialize the distance matrix
distance_matrix = [[0 if i == j else None for j in range(len(tri_state_area_cities))] for i in range(len(tri_state_area_cities))]

# Split the list of cities into chunks of 10
city_chunks = list(chunk_list(tri_state_area_cities, 10))

# Function to make API request.
def make_api_request(origins, destinations):
    params = {
        'origins': '|'.join(origins),
        'destinations': '|'.join(destinations),
        'mode': 'driving',
        'units': 'imperial',
        'language': 'en-US',
        'key': 'AIzaSyDZkzMKatrMp8n2XNQPtC5tdIAOa9l_zSo',
    }
    response = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json', params=params)
    return response.json()

# Making requests for each combination of chunks and updating the distance matrix. Instead of making API requests for every pair, we make requests only for unique combinations. After each request, we update two positions in the matrix - one for the origin-to-destination distance, and one for the destination-to-origin distance.
def make_distance_matrix(tri_state_area_cities):
    city_chunks = list(chunk_list(tri_state_area_cities, 10))
    for i, chunk1 in enumerate(city_chunks):
        for j, chunk2 in enumerate(city_chunks):
            if j >= i:  # Ensure we're not repeating the same pair
                data = make_api_request(chunk1, chunk2)
                if data['status'] == 'OK':
                    for x, origin in enumerate(chunk1):
                        for y, destination in enumerate(chunk2):
                            element = data['rows'][x]['elements'][y]
                            if element['status'] == 'OK':
                                distance = element.get('distance')
                                if distance:
                                    distance_value = int(math.ceil(distance['value'] / 1609.34))  # Convert meters to miles
                                    origin_index = tri_state_area_cities.index(origin)
                                    destination_index = tri_state_area_cities.index(destination)
                                    distance_matrix[origin_index][destination_index] = distance_value
                                    distance_matrix[destination_index][origin_index] = distance_value  # Reflect across diagonal
                                else:
                                    print(f"No road route between {origin} and {destination}")
                            else:
                                print(f"API call failed for {origin} to {destination}")
    return distance_matrix

# Print the distance matrix
def print_matrix(matrix):
    for row in matrix:
        print(row)

def comupte_all():
    tri_state_area_cities = ["New York City NY", "Philadelphia PA", "Stamford CT", "Ithaca NY", "Newark NJ", "Jersey City NJ", "New Brunswick NJ", "Hoboken NJ", "Princeton NJ", "Trenton NJ", "Yonkers NY"]
    
    
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Boston MA")
    tri_state_area_cities.append("Providence RI")
    tri_state_area_cities.append("Hartford CT")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Washington DC")
    tri_state_area_cities.append("Chantilly VA")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Baltimore MD")
    
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Richmond VA")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Virginia Beach VA")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Raleigh NC")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Pittsburgh PA")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Buffalo NY")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Rochester NY")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))
    tri_state_area_cities.append("Syracuse NY")
    all_distance_matrices.append(make_distance_matrix(tri_state_area_cities))  

    return all_distance_matrices


