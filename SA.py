from define_graph import G, Path
from collect_data import demand_filter, standardization_data
import random
import math
# find all possible paths from start node to the node that total stock in node is greater than total value
import json
import pandas as pd


def find_all_paths(graph, start, total_value, material, path=[]):
    path = path + [start]
    if start.get_stock(material) >= total_value:
        return [path]

    total_value -= start.get_stock(material)

    paths = []
    neighbors = graph.get_neighbors(start)
    for node in neighbors:
        if node not in path:
            newPaths = find_all_paths(graph, node, total_value, material, path)
            for newPath in newPaths:
                if newPath not in paths:
                    paths.append(newPath)
    return paths


def find_all_paths_with_cost(graph, start, total_value, material, path=[]):
    paths = find_all_paths(graph, start, total_value, material)
    paths_with_cost = []
    for path in paths:
        paths_with_cost.append(Path(path, material))
    return paths_with_cost


def acceptance_probability(old_cost, new_cost, T):
    if new_cost < old_cost:
        return 1.0
    else:
        return math.exp((old_cost - new_cost)/T)


def random_neighbor(possible_paths, visited):
    if not possible_paths:
        return None
    if len(possible_paths) == 0:
        return None
    if len(possible_paths) == 1:
        return possible_paths[0]
    random_path = random.choice(possible_paths)
    if random_path.name in visited:
        random_neighbor(possible_paths, visited)
    else:
        return random_path


def SA(start, total, material, deadline):
    possible_paths = find_all_paths_with_cost(
        G, start, total, material)
    if not possible_paths:
        return None
    sol = random.choice(possible_paths)
    old_cost = sol.get_path_cost(total, deadline)

    T = 1.0
    T_min = 0.00001
    alpha = 0.9
    visited = []

    while T > T_min:
        i = 1
        while i <= 100:
            new_sol = random_neighbor(possible_paths, visited)
            if new_sol is None:
                return sol
            possible_paths.remove(new_sol)
            visited.append(new_sol.name)
            new_cost = new_sol.get_path_cost(total, deadline)
            ap = acceptance_probability(old_cost, new_cost, T)
            if ap > random.random():
                sol = new_sol
                old_cost = new_cost
            i += 1
        T = T*alpha
    return sol


total_result = []

for demand in demand_filter:
    demand_date, start, demand, material, deadline = standardization_data(
        G, demand)
    prev_deadline = deadline
    # print(start.name, demand, material, deadline)
    # print("From user:" + str(start.name) + " need " + str(demand) +
    #       " of product " + str(material) + " after " + str(deadline) + " days ", end="")
    result = SA(start, demand, material, deadline)
    if result:
        path = ""
        total_cost = result.get_path_cost(demand, deadline)
        for ind, node in enumerate(result.nodes[::-1]):
            if ind == len(result.nodes)-1:  # [C1, D1,D2,D3] => D3->D2->D1->C1
                path += node.name
            else:
                path += node.name + " -> "
        data = {
            'day': demand_date,
            'user': start.name,
            'material': material,
            'demand': demand,
            'deadline': prev_deadline,
            'total_cost(mil VND)': float(total_cost),
            'path': path,
        }
        total_result.append(data)

sum_of_cost = 0
for result in total_result:
    sum_of_cost += float(result['total_cost(mil VND)'])
total = {
    'day': "",
    'user': "",
    'material': "",
    'demand': "",
    'deadline': "TOTAL COST",
    'total_cost(mil VND)': sum_of_cost,
    'path': "",
}

total_result.append(total)

df = pd.DataFrame(total_result)

with open('output_file.csv', 'w', newline='') as file:
    df.to_csv(file, index=False)
print("ok")

# for result in total_result:
#     print("Path:", [node.name for node in result.nodes])
#     print("Total stock:", result.path_cost)
#     print("Total lead time:", result.total_lead_time)
#     print()
