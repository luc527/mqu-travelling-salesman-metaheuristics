import sys
import random

from common import *
from local_search import randomized_local_search

from math import ceil
from heapq import heappush, heappushpop

def greedy(graph: nx.Graph) -> Tuple[float, int]:
    nodes = list(graph.nodes)
    num_nodes = graph.number_of_nodes()

    cycle = []

    marked = {}
    for node in graph.nodes:
        marked[node] = False

    visited = 0

    # Start at 0
    curr_node = nodes[0]
    marked[curr_node] = True
    visited = 1
    cycle.append(curr_node)

    while visited < num_nodes:
        min_adjacent_node = -1
        min_weight = float('inf')
        for other_node in nodes:
            if marked[other_node]:
                continue
            weight = graph.edges[curr_node, other_node]['weight']
            if weight < min_weight:
                min_weight = weight
                min_adjacent_node = other_node
        cycle.append(min_adjacent_node)
        curr_node = min_adjacent_node

        visited += 1
        marked[curr_node] = True
    
    return (evaluate(graph, cycle), cycle)

def greedy_alpha(graph: nx.Graph, alpha: float) -> Tuple[float, list]:
    nodes = list(graph.nodes)
    n = graph.number_of_nodes()

    cycle = []
    cycle_weight = 0

    marked = {}
    for node in nodes:
        marked[node] = False
    visited = 0

    # Start at 0
    curr_node = nodes[0]
    marked[curr_node] = True
    visited = 1
    cycle.append(curr_node)

    while visited < n:

        """
        At each moment we store only the best alpha% nodes seen
        We do that efficiently by storing them in a heap ordered by how bad each node is,
        and maintain the best ones by removing the worst seen so far when we exceed the size of alpha%
        """

        n_left = n - visited
        k = ceil(alpha * n_left)

        bestk = []

        for other_node in nodes:
            if marked[other_node]:
                continue
            weight = graph.edges[curr_node, other_node]['weight']

            if len(bestk) < k:
                heappush(bestk, (-weight, other_node))
            else:
                heappushpop(bestk, (-weight, other_node))

        (neg_weight, chosen_node) = random.choice(bestk)
        cycle.append(chosen_node)
        cycle_weight += -neg_weight

        marked[chosen_node] = True
        visited += 1
        curr_node = chosen_node

    cycle_weight += graph.edges[cycle[-1], cycle[0]]['weight']

    return (cycle_weight, cycle)

def repeated_greedy_alpha(iterations: int, graph: nx.Graph, alpha: float) -> Tuple[float, list]:
    (inc_weight, inc_solution) = greedy_alpha(graph, alpha)
    for _ in range(iterations):
        (weight, solution) = greedy_alpha(graph, alpha)
        if weight < inc_weight:
            inc_weight, inc_solution = weight, solution
    return (inc_weight, inc_solution)

def grasp(iterations: int, graph: nx.Graph, alpha: float) -> Tuple[float, list]:
    (inc_weight, inc_solution) = greedy_alpha(graph, alpha)

    for _ in range(iterations):
        (weight, solution) = greedy_alpha(graph, alpha)
        (weight, solution) = randomized_local_search(iterations, graph, 0.3, solution)
        if weight < inc_weight:
            inc_weight, inc_solution = weight, solution

    return (inc_weight, inc_solution)

def greedy_then_rls(iterations: int, graph: nx.Graph, probability: float):
    (weight, solution) = greedy(graph)
    (weight, solution) = randomized_local_search(iterations, graph, probability, solution)
    return (weight, solution)

if __name__ == '__main__':

    graph = parse_instance(sys.argv[1])

    print('Greedy:')
    (weight, solution) = greedy(graph)
    print(weight, solution)
    print()

    print('Repeated greedy-alpha:')
    (weight, solution) = repeated_greedy_alpha(1000, graph, 0.3)
    print(weight, solution)
    print()

    print('Greedy followed by randomized local search:')
    (weight, solution) = greedy_then_rls(10000, graph, 0.3)
    print(weight, solution)
    print()

    # print('GRASP:')
    # (weight, solution) = grasp(1000, graph, 0.3)
    # print(weight, solution)
    # print()

    #output_image(sys.argv[1], graph, solution)
