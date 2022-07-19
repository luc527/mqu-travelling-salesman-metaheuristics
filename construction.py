import sys
import random

from common import *
from criterion import *
from local_search import randomized_local_search

from math import ceil
from heapq import heappush, heappushpop

"""
Greedy (nearest neighbour)
Greedy-alpha
Repeated greedy (w/ construct_solution as arg)
GRASP (w/ construct_solution AND local_search as args)
"""

def greedy(graph):
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

def greedy_alpha(graph, alpha):
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

"""
Repeated greedy
"""

def repeated_greedy(graph, construct_solution, make_criterion):
    (inc_weight, inc_sol) = construct_solution(graph)
    criterion = make_criterion()
    while not criterion.stop():
        (weight, sol) = construct_solution(graph)
        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol
        criterion.update(inc_weight)
    return (inc_weight, inc_sol)

"""
GRASP
"""

def grasp(graph, construct_solution, local_search, make_criterion):
    (inc_weight, inc_sol) = construct_solution(graph)

    criterion = make_criterion()

    while not criterion.stop():
        (weight, sol) = construct_solution(graph)
        (weight, sol) = local_search(graph, sol)
        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol
        
        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

if __name__ == '__main__':

    filename = sys.argv[1]
    graph = parse_instance(filename)

    iter_crit_ctor = lambda: IterationCriterion(10000)
    time_crit_ctor = lambda: TimeCriterion(60)
    seen_crit_ctor = lambda: TimesSeenBestCriterion(10)

    print(graph)

    print('Greedy:')
    (weight, greedy_sol) = greedy(graph)
    print((weight, greedy_sol), end='\n\n')

    #print('Greedy followed by randomized local search for 1 min:')
    #print(randomized_local_search(graph, 0.4, lambda: TimeCriterion(20), greedy_sol), end='\n\n')

    #print('Repeated greedy-alpha, for 10k iters:')
    #(rga_weight, rga_sol) = repeated_greedy(graph, lambda graph: greedy_alpha(graph, 0.2), lambda: IterationCriterion(10000))
    #print((rga_weight, rga_sol), end='\n\n')

    #print('GRASP for 30 seconds, with randomized local search for 1k iters at each step:')
    #(grasp_weight, grasp_sol) = grasp( \
        #graph, \
        #lambda graph: greedy_alpha(graph, 0.1), \
        #lambda graph, initial: randomized_local_search(graph, 0.4, lambda: IterationCriterion(1000), initial), \
        #lambda: TimeCriterion(30) \
    #)
    #print((grasp_weight, grasp_sol), end='\n\n')

    print('GRASP for 10 iters, with randomized local search for 20 seconds at each step (total 200 secs):')
    (grasp_weight, grasp_sol) = grasp( \
        graph, \
        lambda graph: greedy_alpha(graph, 0.1), \
        lambda graph, initial: randomized_local_search(graph, 0.4, lambda: TimeCriterion(20), initial), \
        lambda: IterationCriterion(10)
    )
    print((grasp_weight, grasp_sol), end='\n\n')

    #output_image(sys.argv[1], graph, solution)
