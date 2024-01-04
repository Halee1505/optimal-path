from define_graph import G, Path
import random
import math
from collect_data import demand_filter, standardization_data
import pandas as pd

# find all paths from start_node to some where that total value of each node is more than total_value


def greedy_algorithm(graph, material, start_node, total_value):
    current_node = start_node
    current_stock = 0
    path = [start_node]
    while current_stock < total_value:
        neighbors = graph.get_neighbors(current_node)
        for neighbor in neighbors:
            neighbor.order = neighbor.get_stock(
                material)/graph.cost_per_ton[(current_node.name, neighbor.name)]
        max_stock_neighbor = max(
            neighbors, key=lambda x: x.order, default=None)

        if max_stock_neighbor is None:
            path = Path(path, material)
            return path, current_stock

        path.append(max_stock_neighbor)
        max_stock_neighbor.order = None
        current_node = max_stock_neighbor
        current_stock += max_stock_neighbor.get_stock(material)

    path = Path(path, material)

    return path, current_stock


total_result = []

for demand in demand_filter:
    demand_date, start, demand, material, deadline = standardization_data(
        G, demand)
    prev_deadline = deadline

    path, current_stock = greedy_algorithm(G, material, start, demand)
    result = path
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
