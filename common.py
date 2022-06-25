from typing import Tuple
import tsplib95 as tsplib
import networkx as nx
import graphviz
import sys
import random
from itertools import permutations

# let's get instances from http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/

def square_matrix(n, x=None):
    m = [[] for _ in range(n)]
    for i in range(n):
        m[i] = [x for _ in range(n)]
    return m

def print_matrix(m):
    for i in range(0, len(m)):
        for j in range(0, len(m[i])):
            print(m[i][j], end='\t')
        print()

def parse_instance(filename):
    problem = tsplib.load(filename)
    g = problem.get_graph()
    return g

def evaluate(graph, solution):
    s = 0
    n = len(solution)
    for i in range(n):
        v = solution[i]
        w = solution[(i+1)%n]
        s += graph.edges[v, w]['weight']
    return s

def brute_force(graph: nx.Graph) -> Tuple[float, list]:
    all_cycles = map(list, permutations(range(graph.number_of_nodes())))
    return min(map(lambda sol: (evaluate(graph, sol), sol), all_cycles))

def neighborhood(solution):
    n = len(solution)
    neighborhood = []
    for i in range(n):
        j = (i + 1) % n
        neighbour = list(solution)
        neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
        neighborhood.append(neighbour)
    return neighborhood

def simple_local_search_impl(graph, solution):
    weight = evaluate(graph, solution)
    iters = 10
    for _ in range(iters):
        nhood = list(map(lambda sol: (evaluate(graph, sol), sol), neighborhood(solution)))
        sub = min(nhood)
        if sub[0] == weight:
            break
        elif sub[0] < weight:
            weight = sub[0]
            solution = sub[1]
    return (weight, solution)


def simple_local_search(graph: nx.Graph) -> Tuple[float, list]:
    initial = [i for i in range(graph.number_of_nodes())]
    random.shuffle(initial)
    return simple_local_search_impl(graph, initial)


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

path = sys.argv[1]

graph = parse_instance(path)

(weight, solution) = simple_local_search(graph)
print(weight, solution)

print(brute_force(graph))

output_image(path, graph, solution)
