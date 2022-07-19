import sys
import random
from common import * 
from criterion import *

"""
Simple local search (w/ select_neighbour as arg)
Multiple start local search (w/ local_search as arg)
Randomized local search
Iterated local search (w/ local_search as arg)
"""

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

def simple_local_search(graph, make_criterion, select_neighbour, initial = None):
    curr_sol = initial if initial is not None else random_cycle(graph.nodes)
    curr_weight = evaluate(graph, curr_sol)

    criterion = make_criterion()

    while not criterion.stop():
        (weight, sol) = select_neighbour(graph, curr_sol, curr_weight)
        if weight == curr_weight: # Local optimum
            break
        elif weight < curr_weight:
            curr_weight, curr_sol = weight, sol

        criterion.update(curr_weight)

    return (curr_weight, curr_sol)

"""
Multiple start local search
"""

def multiple_start_local_search(graph, make_criterion, local_search):
    inc_sol    = random_cycle(graph.nodes)
    inc_weight = evaluate(graph, inc_sol)

    criterion = make_criterion()

    while not criterion.stop():
        sol = random_cycle(graph.nodes)
        (weight, sol) = local_search(graph, sol)
        if weight < inc_weight:
            inc_sol, inc_weight = sol, weight

        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

"""
Randomized local search
"""

def randomized_local_search(graph, probability, make_criterion, initial=None):
    # current solution and its weight
    sol = initial if initial is not None else random_cycle(graph.nodes)
    weight = evaluate(graph, sol)

    # incumbent solution and its weight
    inc_sol = sol
    inc_weight = weight

    criterion = make_criterion()

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

"""
Iterated Local Search
"""

def perturb(solution, perc):
    pd = list(solution) #perturbed
    n = len(solution)
    k = int(n * perc)
    for _ in range(k):
        i = random.randrange(0, n)
        j = (i + 1) % n
        pd[i], pd[j] = pd[j], pd[i]
    return pd


def iterated_local_search(graph, local_search, make_criterion, perturbance_percentage, initial=None):

    initial = initial if initial is not None else random_cycle(graph.nodes)
    (weight, sol) = local_search(graph, initial)
    inc_weight, inc_sol = weight, sol

    # TODO what could this be?
    def accept(weight, sol):
        return True

    criterion = make_criterion()

    while not criterion.stop():
        new_sol = perturb(sol, perturbance_percentage)
        (new_weight, new_sol) = local_search(graph, new_sol)

        if accept(new_weight, new_sol):
            weight, sol = new_weight, new_sol
        if weight < inc_weight:
            inc_weight, inc_sol = weight, sol

        criterion.update(inc_weight)

    return (inc_weight, inc_sol)

if __name__ == '__main__':

    filename = sys.argv[1]
    graph = parse_instance(filename)
    
    initial = random_cycle(graph.nodes)
    #print('Initial random solution:')
    #print((evaluate(graph, initial), initial), end='\n\n')

    #print('Simple local search, for 10k iters (or local optimum found):')
    #print(simple_local_search(graph, lambda: IterationCriterion(10000), best_neighbour, initial), end='\n\n')

    #ls1 = lambda graph, initial: simple_local_search(graph, lambda: IterationCriterion(1000), best_neighbour, initial)
    #print('Multiple start local search for 10 iterations, with 1000-iteration-simple-local-search:')
    #print(multiple_start_local_search(graph, lambda: IterationCriterion(10), ls1), end='\n\n')

    #ls2 = lambda graph, initial: randomized_local_search(graph, 0.4, lambda: IterationCriterion(4000), initial)
    #print('Multiple start local search for 20, iterations, with 4000-iteration-randomized-local-search:')
    #print(multiple_start_local_search(graph, lambda: IterationCriterion(20), ls2), end='\n\n')

    #print('Randomized local search, for 10k iters:')
    #print(randomized_local_search(graph, 0.4, lambda: IterationCriterion(10000), initial), end='\n\n')

    print('Randomized local search, for 1 minute:')
    print(randomized_local_search(graph, 0.4, lambda: TimeCriterion(60), initial), end='\n\n')

    print('Iterated local search (for 1 min, with randomized local search for 2k iters):')
    print(iterated_local_search(\
        graph,\
        lambda graph, initial: randomized_local_search(graph, 0.3, lambda: IterationCriterion(2000), initial),\
        lambda: TimeCriterion(60),\
        0.2,\
        initial\
    ))
