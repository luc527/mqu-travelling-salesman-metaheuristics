import sys
import random
from common import *
from math import ceil
from heapq import heappush, heappushpop

def greedy_cycle(graph: nx.Graph) -> Tuple[float, int]:
    nodes = graph.number_of_nodes()

    cycle = []

    marked = [False for _ in range(nodes)]
    visited = 0

    # Start at 0
    curr_node =  0
    marked[curr_node] = True
    visited = 1
    cycle.append(curr_node)

    while visited < nodes:
        min_adjacent_node = -1
        min_weight = float('inf')
        for other_node in range(nodes):
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

def greedy_alpha_cycle(graph: nx.Graph, alpha: float) -> Tuple[float, list]:
    n = graph.number_of_nodes()
    cycle = []
    cycle_weight = 0

    marked  = [False for _ in range(n)]
    visited = 0

    # Start at 0
    curr_node = 0
    marked[0] = True
    visited = 1
    cycle.append(0)

    while visited < n:

        """
        At each moment we store only the best alpha% nodes seen
        We do that efficiently by storing them in a heap ordered by how bad each node is,
        and maintain the best ones by removing the worst seen so far when we exceed the size of alpha%
        """

        n_left = n - visited
        k = ceil(alpha * n_left)

        bestk = []

        for other_node in range(n):
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



graph = parse_instance(sys.argv[1])

(weight, solution) = greedy_cycle(graph)
print('Greedy:')
print(weight, solution)
print()

(weight, solution) = greedy_alpha_cycle(graph, 0.2)
print('Greedy-alpha:')
print(weight, solution)
print()

#output_image(sys.argv[1], graph, solution)
