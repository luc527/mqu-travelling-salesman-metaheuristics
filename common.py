from typing import Tuple
import tsplib95 as tsplib
import networkx as nx
import graphviz
import random
from itertools import permutations

# let's get instances from http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/

def output_image(filepath: str, graph: nx.Graph, cycle: list):
    lastidx = -1
    for i, c in enumerate(filepath):
        if c == '/':
            lastidx = i
    filepath = filepath[lastidx+1:]

    verts = graph.number_of_nodes()

    cycle_edges = list(zip(cycle, [cycle[-1]] + cycle[:-1]))

    viz = graphviz.Graph(filepath)
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
    print(f'Rendered graph on {filepath}, see {viz.render(directory=dir)}') 

def parse_instance(filename):
    return tsplib.load(filename).get_graph()

def brute_force(g: nx.Graph) -> Tuple[float, list]:
    all_cycles = map(list, permutations(range(g.number_of_nodes())))
    return min(map(lambda s: (evaluate(g, s), s), all_cycles))

def random_walk(iterations: int, g: nx.Graph) -> Tuple[float, list]:
    n = g.number_of_nodes()
    sol = random_cycle(n)
    for _ in range(iterations):
        v = random.randrange(0, n)
        w = (v + 1) % n
        sol[v], sol[w] = sol[w], sol[v]
    return (evaluate(g, sol), sol)


def evaluate(graph, solution):
    s = 0
    n = len(solution)
    for i in range(n):
        v = solution[i]
        w = solution[(i+1)%n]
        s += graph.edges[v, w]['weight']
    return s

def random_cycle(n):
    solution = list(range(n))
    random.shuffle(solution)
    return solution

