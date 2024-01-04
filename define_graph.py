from collections import deque
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

from collect_data import cost_data, stock_data

PENALTY_PRICE = 0.1


class Point:

    def __init__(self, type, name):
        self.type = type
        self.name = name
        self.stock = {}
        self.next = None

    def add_next(self, next):
        self.next = next

    def add_stock(self, material, stock):
        self.stock[int(material)] = int(stock)

    def get_stock(self, material):
        return self.stock.get(material, 0)


class Path:
    nodes = []
    path_cost = 0
    name = ""
    total_lead_time = 0

    def __init__(self, nodes, material):
        for node in nodes:
            self.name += node.name

        for i in range(len(nodes)-1):
            self.path_cost += G.get_cost(
                nodes[i], nodes[i+1])

        if len(nodes) > 1:
            for i in range(len(nodes)-1):
                self.total_lead_time += G.lead_time[(
                    nodes[i].name, nodes[i+1].name)]

        self.nodes = nodes

    def get_path_cost(self, total_value, deadline):

        if self.total_lead_time > deadline:

            return round(self.path_cost * total_value + PENALTY_PRICE*(self.total_lead_time - deadline), 2)
        return round(self.path_cost * total_value, 2)


class Graph:
    nodes = []
    edges = []
    cost_per_ton = {}
    lead_time = {}

    def add_node(self, node):
        self.nodes.append(node)

    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node

        return None

    def add_edge(self, from_node, to_node, lead_time, cost_per_ton):
        self.edges.append((from_node, to_node))
        self.edges.append((to_node, from_node))
        self.lead_time[(from_node.name, to_node.name)] = lead_time
        self.lead_time[(to_node.name, from_node.name)] = lead_time
        self.cost_per_ton[(from_node.name, to_node.name)] = cost_per_ton
        self.cost_per_ton[(to_node.name, from_node.name)] = cost_per_ton

    def get_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge[0].name == node.name:
                if node.type == "C" and edge[1].type == "D":
                    neighbors.append(edge[1])
                if node.type == "D" and edge[1].type != "C":
                    neighbors.append(edge[1])
                if node.type == "P" and edge[1].type == "P":
                    neighbors.append(edge[1])
        return neighbors

    def get_weight(self, from_node, to_node, material):

        return self.cost_per_ton[(from_node.name, to_node.name)] * material

    def get_cost(self, from_node, to_node):
        return self.cost_per_ton[(from_node.name, to_node.name)]

    def draw_diagram(self):
        graph = nx.Graph()
        for i in range(len(self.nodes)):
            graph.add_node(self.nodes[i].name, layer=self.nodes[i].type)
        for i in range(len(self.edges)):
            graph.add_edge(self.edges[i][0].name, self.edges[i][1].name, weight=str(
                self.cost_per_ton[(self.edges[i][0].name, self.edges[i][1].name)]) + "mil/VND" + " " + str(self.lead_time[(self.edges[i][0].name, self.edges[i][1].name)]) + "day")

        pos = nx.multipartite_layout(graph, subset_key="layer", scale=0.2)
        nx.draw_networkx_nodes(graph, pos)
        nx.draw_networkx_labels(graph, pos)
        edges = [(self.edges[i][0].name, self.edges[i][1].name)
                 for i in range(len(self.edges))]
        nx.draw_networkx_edges(graph, pos, edgelist=edges,
                               edge_color="skyblue", width=1)
        edge_labels = {(self.edges[i][0].name, self.edges[i][1].name):
                       str(self.cost_per_ton[(
                           self.edges[i][0].name, self.edges[i][1].name)])
                       + "mil/VND" + " " +
                       str(self.lead_time[(
                           self.edges[i][0].name, self.edges[i][1].name)]) + "day"
                       for i in range(len(self.edges))
                       }
        edge_label_pos = pos
        nx.draw_networkx_edge_labels(
            graph, edge_label_pos, edge_labels=edge_labels)
        plt.show()

    def print_graph(self):
        for node in self.nodes:
            print(node.name, end="-----")
            for neighbor in self.get_neighbors(node):
                print(
                    self.lead_time[(node.name, neighbor.name)], end="(day)-----")
                print(
                    self.cost_per_ton[(node.name, neighbor.name)], end="(mil/VND)-----")
                print(neighbor.name, end=" ")
            print()


G = Graph()
P1 = Point("P", "P1")
P2 = Point("P", "P2")
D1 = Point("D", "D1")
D2 = Point("D", "D2")
D3 = Point("D", "D3")

C1 = Point("C", "C1")
C2 = Point("C", "C2")
C3 = Point("C", "C3")
C4 = Point("C", "C4")
C5 = Point("C", "C5")
C6 = Point("C", "C6")
C7 = Point("C", "C7")
C8 = Point("C", "C8")
C9 = Point("C", "C9")
C10 = Point("C", "C10")

G.add_node(P1)
G.add_node(P2)
G.add_node(D1)
G.add_node(D2)
G.add_node(D3)
G.add_node(C1)
G.add_node(C2)
G.add_node(C3)
G.add_node(C4)
G.add_node(C5)
G.add_node(C6)
G.add_node(C7)
G.add_node(C8)
G.add_node(C9)
G.add_node(C10)

for datum in cost_data:
    G.add_edge(G.get_node(datum[2]), G.get_node(datum[3]), datum[4], datum[5])

for stock in stock_data:
    G.get_node(stock[2]).add_stock(stock[1], stock[4])


G.draw_diagram()
