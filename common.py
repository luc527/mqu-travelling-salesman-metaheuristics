# TODO random walk

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

def random_walk(g: nx.Graph) -> Tuple[float, list]:
    # TODO
    pass

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

def random_cycle(n):
    solution = list(range(n))
    random.shuffle(solution)
    return solution

# sls: simple local search

# TODO make sls as a function that takes a neighborhood selection strategy (another function)

"""
Busca local simples com melhor melhora
"""
def sls_best(graph: nx.Graph) -> Tuple[float, list]:
    global iterations

    curr_solution = random_cycle(graph.number_of_nodes())
    curr_weight   = evaluate(graph, curr_solution)

    for _ in range(iterations):
        best_solution = curr_solution
        best_weight   = curr_weight
        for solution in neighborhood(curr_solution):
            weight = evaluate(graph, solution)
            if weight < best_weight:
                best_solution = solution
                best_weight = weight

        curr_solution = best_solution
        curr_weight = best_weight

    return (curr_weight, curr_solution)


"""
Busca local simples com primeira melhora
"""
def sls_first(graph: nx.Graph) -> Tuple[float, list]:
    global iterations

    curr_solution = random_cycle(graph.number_of_nodes())
    curr_weight   = evaluate(graph, curr_solution)

    for _ in range(iterations):
        for solution in neighborhood(curr_solution):
            weight = evaluate(graph, solution)
            if weight < curr_weight:
                curr_solution = solution
                curr_weight   = weight
                break

    return (curr_weight, curr_solution)


path = sys.argv[1]

iterations = int(sys.argv[2]) if len(sys.argv) > 1 else 65536

graph = parse_instance(path)

print('Busca local simples com primeira melhora:')
print(sls_first(graph))

print('Busca local simples com melhor melhora:')
print(sls_best(graph))

#print('Solução ótima por força bruta:')
#print(brute_force(graph))

# output_image(path, graph, solution)
