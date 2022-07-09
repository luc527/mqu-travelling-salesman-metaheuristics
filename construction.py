import sys
import random

from common import *
from criterion import *
from local_search import randomized_local_search

from math import ceil
from heapq import heappush, heappushpop

"""
Greedy and semi-greedy (alpha) algorithms (closest neighbour at each step)
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

"""
Repeated greedy
"""

def repeated_greedy_alpha(graph, alpha, criterion_thunk):
    criterion = criterion_thunk()

    (inc_weight, inc_sol) = greedy_alpha(graph, alpha)
    while not criterion.stop():
        (weight, sol) = greedy_alpha(graph, alpha)
        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol
        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

def grasp_alpha(graph, alpha, criterion_thunk, rls_probability, rls_criterion_thunk):
    (inc_weight, inc_sol) = greedy_alpha(graph, alpha)

    criterion = criterion_thunk()
    while not criterion.stop():
        (weight, sol) = greedy_alpha(graph, alpha)
        (weight, sol) = randomized_local_search(graph, rls_probability, rls_criterion_thunk, sol)
        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol
        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

if __name__ == '__main__':

    filename = sys.argv[1]
    graph = parse_instance(filename)

    print(graph)

    print('Greedy:')
    (weight, greedy_sol) = greedy(graph)
    print(weight, greedy_sol, end='\n\n')

    iter_crit_thunk = lambda: IterationCriterion(10000)
    time_crit_thunk = lambda: TimeCriterion(60)
    seen_crit_thunk = lambda: TimesSeenBestCriterion(10)

    #print('Repeated greedy-alpha, for 10k iters:')
    #print(repeated_greedy_alpha(graph, 0.2, iter_crit_thunk), end='\n\n')

    #print('Repeated greedy-alpha, for 1 minute:')
    #print(repeated_greedy_alpha(graph, 0.2, time_crit_thunk), end='\n\n')

    #print('Repeated greedy-alpha, after seeing the best solution 10 times:')
    #print(repeated_greedy_alpha(graph, 0.2, seen_crit_thunk), end='\n\n')

    #print('GRASP for 1 minute, with randomized local search for 1k iters at each step:')
    #print(grasp_alpha(graph, 0.2, lambda: TimeCriterion(60), 0.4, lambda: IterationCriterion(1000)))
    ## This is an example of where the time criterion implementation is imprecise
    # after 59 seconds it may start a randomized local search with 1k iters
    # then it has to perform the whole randomized local search, which might take
    # like 10 seconds, before checking again for the time criterion, so it
    # actually runs for 1 min 9 secs

    #print('GRASP for 20 iters, with randomized local search for 10 secs at each step (200 secs total!):')
    #print(grasp_alpha(graph, 0.2, lambda: IterationCriterion(20), 0.4, lambda: TimeCriterion(10)), end='\n\n')

    #print('GRASP (with greedy-alpha) for 10 iters, with randomized local search for 10 secs at each step (100 secs total):')
    #print(grasp_alpha(graph, 0.2, lambda: IterationCriterion(10), 0.4, lambda: TimeCriterion(10)), end='\n\n')

    #print('Greedy followed by randomized local search for 1 min:')
    #print(randomized_local_search(graph, 0.4, time_crit_thunk, greedy_sol), end='\n\n')

    #output_image(sys.argv[1], graph, solution)
