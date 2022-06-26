from typing import Tuple
import tsplib95 as tsplib
import networkx as nx
import graphviz
import sys
import random
from itertools import permutations

# let's get instances from http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/

def output_image(path, graph, cycle):
    lastidx = -1
    for i, c in enumerate(path):
        if c == '/':
            lastidx = i
    path = path[lastidx+1:]

    verts = graph.number_of_nodes()

    cycle_edges = list(zip(cycle, [cycle[-1]] + cycle[:-1]))

    viz = graphviz.Graph(path)
    # viz.attr('node', {'shape': 'point'})
    viz.attr('edge', {'fontsize': '8'})
    for a in range(verts):
        viz.node(str(a))
    for b in range(verts):
        for a in range(b):
            label = str(graph.edges[a,b]['weight'])
            attr = {}
            if (a, b) in cycle_edges or (b, a) in cycle_edges:
                attr['color'] = 'red'
                attr['penwidth'] = '3'
            viz.edge(str(a), str(b), label, attr)
    dir = 'images'
    print(f'Rendered graph on {path}, see {viz.render(directory=dir)}') 

def parse_instance(filename):
    return tsplib.load(filename).get_graph()

def brute_force(g: nx.Graph) -> Tuple[float, list]:
    all_cycles = map(list, permutations(range(g.number_of_nodes())))
    return min(map(lambda s: (evaluate(g, s), s), all_cycles))

def evaluate(graph, solution):
    s = 0
    n = len(solution)
    for i in range(n):
        v = solution[i]
        w = solution[(i+1)%n]
        s += graph.edges[v, w]['weight']
    return s

def neighborhood(solution):
    n = len(solution)
    neighborhood = []
    for i in range(n):
        j = (i + 1) % n
        nb = list(solution)
        nb[i], nb[j] = nb[j], nb[i]
        neighborhood.append(nb)
    return neighborhood

def simple_local_search(graph: nx.Graph) -> Tuple[float, list]:
    # Initial solution: random cycle
    solution = [i for i in range(graph.number_of_nodes())]
    random.shuffle(solution)
    weight = evaluate(graph, solution)

    # Stop criteria: # of iterations
    for _ in range(1000):
        best = min(map( \
            lambda sol: (evaluate(graph, sol), sol), \
            neighborhood(solution) \
        ))
        if best[0] < weight:
            (weight, solution) = best
    return (weight, solution)


path = sys.argv[1]

graph = parse_instance(path)

(weight, solution) = simple_local_search(graph)
print(weight, solution)

print(brute_force(graph))

output_image(path, graph, solution)
