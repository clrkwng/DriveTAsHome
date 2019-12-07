import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils
import random
import math
import time
from copy import deepcopy

from student_utils import *
from output_validator import *
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
    FWdict = nx.floyd_warshall(G)

    global_best_tour = []
    global_best_cost = 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    local_best_tour = global_best_tour
    local_best_cost = global_best_cost

    starting_car_location = convert_locations_to_indices([starting_car_location], list_of_locations)[0]
    list_of_homes = convert_locations_to_indices(list_of_homes, list_of_locations)
    list_of_locations = convert_locations_to_indices(list_of_locations, list_of_locations)

    coolingRate = 0.97
    ITERATIONS = 10000
    temp_original = 10000

    for size in range(0, len(list_of_homes)):
        temp = temp_original
        indices = [i for i in range(len(list_of_locations)) if i != starting_car_location]

        # tour is current tour we are considering
        tour = [starting_car_location]
        tour += (indices[:size])
        if size > 0:
            tour.append(starting_car_location)

        # notInTour is all the vertices outside current tour
        notInTour = indices[size:]
        local_best_tour = tour
        local_best_cost = cost_of_cycle(list_of_homes, G, tour, FWdict)

        for i in range(ITERATIONS):
            if size == 0:
                continue
            switch1 = random.randint(1, size)
            switch2 = random.randint(1, len(list_of_locations) - 1)
            switch2InTour = True
            if switch2 > size:
                switch2 -= size + 1
                switch2InTour = False
            if switch2InTour:
                tour[switch1], tour[switch2] = tour[switch2], tour[switch1]
            else:
                tour[switch1], notInTour[switch2] = notInTour[switch2], tour[switch1]

            curr_cost = cost_of_cycle(list_of_homes, G, tour, FWdict)
            change_cost = curr_cost - local_best_cost

            if change_cost < 0:
                local_best_cost = curr_cost
                local_best_tour = tour
            elif random.random() < math.exp(-(change_cost/temp)):
                local_best_cost = curr_cost
                local_best_tour = tour
            else:
                if switch2InTour:
                    tour[switch1], tour[switch2] = tour[switch2], tour[switch1]
                else:
                    tour[switch1], notInTour[switch2] = notInTour[switch2], tour[switch1]

            temp *= coolingRate

        if local_best_cost < global_best_cost:
            global_best_tour = local_best_tour
            global_best_cost = local_best_cost

        print(str(size) + " : " + str(global_best_cost))
        print("Best tour: " + str(global_best_tour))
        print()

    dropoff_mapping = drop_off_given_path(global_best_tour, list_of_homes, FWdict)
    validTour = []
    
    #returns the actual valid tour from G
    for u, v in zip(global_best_tour[:-1], global_best_tour[1:]):
        validTour += (nx.shortest_path(G, source = u, target = v, weight='weight'))[:-1]
    validTour.append(starting_car_location)
    return validTour, dropoff_mapping

def cost_of_cycle(list_of_homes, G, car_cycle, FWdict):
    dropoff_mapping = drop_off_given_path(car_cycle, list_of_homes, FWdict)
    ret, msg = cost_of_cycle_helper(G, car_cycle, dropoff_mapping, FWdict)
    return ret

def cost_of_cycle_helper(G, car_cycle, dropoff_mapping, FWdict):
    cost = 0
    message = ''
    dropoffs = dropoff_mapping.keys()

    if not car_cycle[0] == car_cycle[-1]:
        message += 'The start and end vertices are not the same.\n'
        cost = 'infinite'
    if cost != 'infinite':
        if len(car_cycle) == 1:
            car_cycle = []
        else:
            car_cycle = get_edges_from_path(car_cycle[:-1]) + [(car_cycle[-2], car_cycle[-1])]
        if len(car_cycle) != 1:
            driving_cost = sum([FWdict[e[0]][e[1]] for e in car_cycle]) * 2 / 3
        else:
            driving_cost = 0
        walking_cost = 0
        shortest = FWdict

        for drop_location in dropoffs:
            for house in dropoff_mapping[drop_location]:
                walking_cost += shortest[drop_location][house]

        message += f'The driving cost of your solution is {driving_cost}.\n'
        message += f'The walking cost of your solution is {walking_cost}.\n'
        cost = driving_cost + walking_cost

    message += f'The total cost of your solution is {cost}.\n'
    return cost, message

def drop_off_given_path(path, homes, FWdict):
    vert_dict = {}
    for vert in path:
        vert_dict[vert] = []
    for home in homes:
        best_dist = 10000000000000000
        best_vert = path[0]
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

def main():
    print("Test")



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

    #getting the new cost
    G, _ = adjacency_matrix_to_graph(adjacency_matrix)
    curr_cost, _ = cost_of_solution(G, car_path, drop_offs)

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    #checking if new cost is better or not
    if os.path.isfile(output_file):
        output_data = utils.read_file(output_file)
        best_cost, _ = tests(input_data, output_data)
        if curr_cost < best_cost:
            convertToFile(car_path, drop_offs, output_file, list_locations)
        print('Best cost so far: ' + str(best_cost), ', New cost: ' + str(curr_cost))
    else:
        convertToFile(car_path, drop_offs, output_file, list_locations)
        print('New cost: ' + str(curr_cost))


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