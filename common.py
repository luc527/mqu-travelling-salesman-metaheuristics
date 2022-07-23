from typing import Tuple
import tsplib95 as tsplib
import networkx as nx
import random
from itertools import permutations

def parse_instance(filename):
    return tsplib.load(filename).get_graph()

def brute_force(g: nx.Graph) -> Tuple[float, list]:
    all_cycles = map(list, permutations(list(g.nodes)))
    return min(map(lambda s: (evaluate(g, s), s), all_cycles))

def random_walk(graph, make_criterion):
    n = graph.number_of_nodes()
    sol = random_cycle(graph.nodes)
    weight = evaluate(graph, sol)
    criterion = make_criterion()
    while not criterion.stop():
        v = random.randrange(0, n)
        w = (v + 1) % n
        sol[v], sol[w] = sol[w], sol[v]
        weight = evaluate(graph, sol)
        criterion.update(weight)
    return (weight, sol)


def evaluate(graph, solution):
    s = 0
    n = len(solution)
    for i in range(n):
        v = solution[i]
        w = solution[(i+1)%n]
        s += graph.edges[v, w]['weight']
    return s

def random_cycle(nodes):
    nodes = list(nodes)
    random.shuffle(nodes)
    return nodes

