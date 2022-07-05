import sys
from common import *

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

# TODO implement greedy-alpha

# -> get from the best k at *each step* (each for other_node ...)

graph = parse_instance(sys.argv[1])
(weight, solution) = greedy_cycle(graph)

print((weight, solution))

output_image(sys.argv[1], graph, solution)
