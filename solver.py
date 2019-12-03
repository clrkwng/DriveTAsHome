import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import random
import math
import time

from DriveTAsHome.student_utils import *
"""
======================================================================
  Complete the following function.
======================================================================
"""

def solve(list_of_locations, list_of_homes, starting_car_location, adjacency_matrix, params=[]):
    """
    Write your algorithm here.
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """
    G, msg = adjacency_matrix_to_graph(adjacency_matrix)
    # if msg != "":
    #     return
    #raise error as a location has a road to self
    coolingRate = 0.97
    ITERATIONS = 10
    temp_original = 10000

    FWdict = nx.floyd_warshall(G)
    global_best_tour = []
    global_best_cost = 10000000000000000000000000000000000000000000000000000000000000000000
    local_best_tour = global_best_tour
    local_best_cost = global_best_cost
    starting_car_location = convert_locations_to_indices([starting_car_location], list_of_locations)[0]
    list_of_homes = convert_locations_to_indices(list_of_homes, list_of_locations)
    list_of_locations = convert_locations_to_indices(list_of_locations, list_of_locations)

    for size in range(0, len(list_of_locations)//2):
        temp = temp_original

        tour = get_two_tours(adjacency_matrix, starting_car_location, size)
        if not tour:
            continue
        tour1_cost = cost_of_cycle(list_of_homes, G, tour[0], FWdict)
        tour2_cost = cost_of_cycle(list_of_homes, G, tour[1], FWdict)

        if tour1_cost <= tour2_cost:
            tour = tour[0]
        else:
            tour = tour[1]

        for i in range(ITERATIONS):
            tour = switch_vertex(G, tour)
            tour = switch_edges(G, tour)
            curr_cost = cost_of_cycle(list_of_homes, G, tour, FWdict)
            change_cost = curr_cost - local_best_cost

            if change_cost < 0:
                #switch based on temperature?
                local_best_cost = curr_cost
                local_best_tour = tour
            elif random.random() < math.exp(-(change_cost/temp)):
                local_best_cost = curr_cost
                local_best_tour = tour

            temp *= coolingRate

        if local_best_cost < global_best_cost:
            global_best_tour = local_best_tour
            global_best_cost = local_best_cost

        print(str(size) + " : " + str(global_best_cost))

    dropoff_mapping = drop_off_given_path(global_best_tour, list_of_homes, FWdict)
    return global_best_tour, dropoff_mapping

def cost_of_cycle(list_of_homes, G, car_cycle, FWdict):
    dropoff_mapping = drop_off_given_path(car_cycle, list_of_homes, FWdict)
    ret, msg = cost_of_solution(G, car_cycle, dropoff_mapping)
    return ret

def get_neighbors(v, adj_matrix):
    lst = []
    for i in range(len(adj_matrix[v])):
        if adj_matrix[v][i] != 'x':
            lst.append(i)
    return lst

#returns a tour with repeated vertices
def pick_tour_with_repeats(starting_car_location, adj_matrix, all_paths, length, timer):
    path = []
    pick_tour_with_repeats_helper(adj_matrix, length, starting_car_location, starting_car_location, path, all_paths, timer)

def pick_tour_with_repeats_helper(adj_matrix, length, v, starting_car_location, path, all_paths, timer):
    if length == -1 and v == starting_car_location:
        all_paths.append(path)
        return
    elif length == -1:
        return

    neighbors = get_neighbors(v, adj_matrix)
    random.shuffle(neighbors)

    for u in neighbors:
        path.append(u)
        curr = time.time()
        if (curr - timer) > 5:
            return []
        pick_tour_with_repeats_helper(adj_matrix, length - 1, u, starting_car_location, path, all_paths, timer)
        if len(all_paths) != 0:
            return
        path.pop()

#returns a tour with no repeated vertices
def pick_tour_without_repeats(starting_car_location, adj_matrix, all_paths, length, timer):
    path = []
    visited = set([starting_car_location])
    pick_tour_without_repeats_helper(adj_matrix, length, starting_car_location, starting_car_location, path, all_paths, visited, timer)

def pick_tour_without_repeats_helper(adj_matrix, length, v, starting_car_location, path, all_paths, visited, timer):
    if length == -1 and v == starting_car_location:
        # if len(set(path)) == len(path):
        #     all_paths.append(path)
        #     return
        # else:
        #     return
        all_paths.append(path)
        return
    elif length == -1:
        return

    neighbors = get_neighbors(v, adj_matrix)
    random.shuffle(neighbors)

    for u in neighbors:
        if length == 0 or u not in visited:
            path.append(u)
            visited.add(u)
            curr = time.time()
            if (curr - timer) > 5:
                return []
            pick_tour_without_repeats_helper(adj_matrix, length - 1, u, starting_car_location, path, all_paths, visited, timer)
            if len(all_paths) != 0:
                return
            if u in visited:
                visited.remove(u)
            path.pop()

#returns a list of two tours: one with repeats, and one without repeats
def get_two_tours(adj_matrix, starting_car_location, length):
    path = []
    start = time.time()
    pick_tour_with_repeats(starting_car_location, adj_matrix, path, length, start)

    if len(path) != 0:
        path[0].insert(0, starting_car_location)
    else:
        path.append([starting_car_location])

    path2 = []
    start = time.time()
    pick_tour_without_repeats(starting_car_location, adj_matrix, path2, length, start)
    if len(path2) != 0:
        path2[0].insert(0, starting_car_location)
    else:
        path2.append([starting_car_location])

    return [path[0], path2[0]]


def drop_off_given_path(path, homes, FWdict):
    vert_dict = {}
    total_dist = 0
    for vert in path:
        vert_dict[vert] = []
    for home in homes:
        best_dist = 10000000
        best_vert = 0
        for vert in path:
            temp_dist = FWdict[vert][home]
            if temp_dist < best_dist:
                best_vert = vert
                best_dist = temp_dist
        vert_dict[best_vert].append(home)
    final_dict = {}
    for vert in path:
        if vert_dict[vert] != []:
            final_dict[vert] = vert_dict[vert]
    return final_dict

def switch_vertex(G, tour):
    """
    Input:
        G: Original Graph
        tour: List of
    Output:
        Generate a new tour where two of the vertices are switched
    """
    noOfSwitchableVertices = len(tour) - 1

    indices = list(range(1, noOfSwitchableVertices))
    random.shuffle(indices)

    for index in indices:
        neighbors0 = G.neighbors(tour[index - 1])
        neighbors1 = G.neighbors(tour[index + 1])

        common = [vertex for vertex in neighbors0 if vertex in neighbors1]
        if len(common) > 0:
            tour[index] = random.choice(common)
            return tour

    return tour


def switch_edges(G, tour):
    #find appropriate switches
    #find two pairs of cosecutive vertices
    #check to see if x1 connects to y1 and x2 connects to y2
    #have to translate that into the tour
    # tour now goes from s -> x1 -> reverse[x2:y1] -> y2 -> s

    noOfSwitchableVertices = len(tour) - 1

    indices = list(range(1, noOfSwitchableVertices))
    random.shuffle(indices)

    #need to check if it's greater than 4?

    for x in range(len(indices) - 1):
        edge1 = G.has_edge(tour[indices[x]], tour[indices[x+1]])
        edge2 = G.has_edge(tour[indices[x] + 1], tour[indices[x+1] + 1])

        if edge1 and edge2:
            x1 = min(indices[x], indices[x+1])
            y1 = max(indices[x], indices[x+1])

            first = tour[:x1 + 1]
            reverse = tour[x1 + 1: y1 + 1]
            reverse = reverse[::-1]
            end = tour[y1 + 1:]

            tour = first + reverse + end

    return tour

def main():
    adj_matrix = [
        ['x', 2.88966, 'x', 'x', 3.78423, 'x', 'x', 'x', 'x', 'x'],
        [2.88966, 'x', 4.17414, 6.25644, 3.1229, 'x', 2.69494, 5.35798, 'x', 'x'],
        ['x', 4.17414, 'x', 'x', 'x', 2.02081, 'x', 'x', 'x', 'x'],
        ['x', 6.25644, 'x', 'x', 'x', 'x', 'x', 'x', 'x', 2.07271],
        [3.78423, 3.1229, 'x', 'x', 'x', 0.96957, 3.36051, 'x', 1.82842, 'x'],
        ['x', 'x', 2.02081, 'x', 0.96957, 'x', 'x', 4.50784, 'x', 'x'],
        ['x', 2.69494, 'x', 'x', 3.36051, 'x', 'x', 'x', 3.98942, 'x'],
        ['x', 5.35798, 'x', 'x', 'x', 4.50784, 'x', 'x', 4.96827, 'x'],
        ['x', 'x', 'x', 'x', 1.82842, 'x', 3.98942, 4.96827, 'x', 5.47821],
        ['x', 'x', 'x', 2.07271, 'x', 'x', 'x', 'x', 5.47821, 'x']
    ]

    starting_car_location = 1

    #length is the number of vertices visited, excluding starting_car_location
    length = 5

    #paths[0] is tour with repeats, paths[1] is tour without repeats
    # G, msg = adjacency_matrix_to_graph(adj_matrix)
    # paths = get_two_tours(adj_matrix, starting_car_location, length)
    # print('Tour with repeats: ' + str(paths[0]))
    # print('Tour without repeats: ' + str(paths[1]))
    # print(switch_vertex(G, paths[0]))
    # print(switch_edges(G, paths[0]))
    list_of_homes = [0, 4, 5, 8]
    list_of_locations = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    tour, dropoff_location = solve(list_of_locations, list_of_homes, 1, adj_matrix)
    print(tour)
    print(dropoff_location)

#main()


"""
======================================================================
   No need to change any code below this line
======================================================================
"""

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')

    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
