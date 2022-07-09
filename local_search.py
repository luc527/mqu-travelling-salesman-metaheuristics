import sys
import random
from common import * 
from criterion import *

def neighborhood(solution):
    n = len(solution)
    for i in range(n):
        j = (i + 1) % n
        nb = list(solution)
        nb[i], nb[j] = nb[j], nb[i]
        yield nb

"""
Neighbour selection strategies
"""

def first_better_neighbour(graph, curr_solution, curr_weight):
    for neighbour in neighborhood(curr_solution):
        weight = evaluate(graph, neighbour)
        if weight < curr_weight:
            return (weight, neighbour)
    return (curr_weight, curr_solution)

def best_neighbour(graph, curr_solution, curr_weight):
    best_solution = curr_solution
    best_weight = curr_weight

    for neighbour in neighborhood(curr_solution):
        weight = evaluate(graph, neighbour)
        if weight < best_weight:
            best_solution = neighbour
            best_weight   = weight

    return (best_weight, best_solution)

def random_neighbour(graph, solution):
    n = len(solution)
    i = random.randrange(0, n)
    j = (i + 1) % n
    nb = list(solution)
    nb[i], nb[j] = nb[j], nb[i]
    return (evaluate(graph, nb), nb)

"""
Simple local search
"""

def simple_local_search(select_neighbour):
    def sls(graph, criterion_thunk, initial = None):
        curr_sol = initial if initial is not None else random_cycle(graph.nodes)
        curr_weight = evaluate(graph, curr_sol)

        criterion = criterion_thunk()

        while not criterion.stop():
            (weight, sol) = select_neighbour(graph, curr_sol, curr_weight)
            if weight == curr_weight:
                # Local optimum
                break
            elif weight < curr_weight:
                curr_weight, curr_sol = weight, sol

            criterion.update(curr_weight)

        return (curr_weight, curr_sol)
    return sls

"""
Randomized local search
"""

def randomized_local_search(graph, probability, criterion_thunk, initial=None):

    # current solution and its weight
    sol = initial if initial is not None else random_cycle(graph.nodes)
    weight = evaluate(graph, sol)

    # incumbent solution and its weight
    inc_sol = sol
    inc_weight = weight

    criterion = criterion_thunk()

    while not criterion.stop():
        r = random.random()

        if r <= probability:
            (weight, sol) = random_neighbour(graph, sol)
        else:
            (next_weight, next_sol) = best_neighbour(graph, sol, weight)
            if next_weight == weight:  # local optimum
                (weight, sol) = random_neighbour(graph, sol)
            else:
                weight, sol = next_weight, next_sol

        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol

        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

if __name__ == '__main__':
    # run for 10k iters
    iter_crit_thunk = lambda: IterationCriterion(10000)

    # run for 1 min
    time_crit_thunk = lambda: TimeCriterion(60)

    # stop after seeing the best solution 1000 times
    seen_crit_thunk = lambda: TimesSeenBestCriterion(1000)


    filename = sys.argv[1]
    graph = parse_instance(filename)
    print(graph)

    sls = simple_local_search(best_neighbour)

    #print('Simple local search, for 10k iters (or local optimum found):')
    #print(sls(graph, iter_crit_thunk), end='\n\n')

    #print('Simple local search, for 1 minute (or local optimum found):')
    #print(sls(graph, time_crit_thunk), end='\n\n')

    #print('Simple local search, after seeing the best solution 1000 times (or local optimum found):')
    #print(sls(graph, seen_crit_thunk), end='\n\n')

    #print('Randomized local search, for 10k iters:')
    #print(randomized_local_search(graph, 0.4, iter_crit_thunk), end='\n\n')

    #print('Randomized local search, for 1 minute:')
    #print(randomized_local_search(graph, 0.4, time_crit_thunk), end='\n\n')

    #print('Randomized local search, after seeing the best solution 1000 times:')
    #print(randomized_local_search(graph, 0.4, seen_crit_thunk), end='\n\n')