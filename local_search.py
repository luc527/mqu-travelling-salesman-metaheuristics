import sys
from common import * 

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
    def sls_with_given_select_fn(iterations: int, graph: nx.Graph, initial_solution: list = None) -> Tuple[float, list]:

        curr_solution = initial_solution if initial_solution is not None else random_cycle(graph.number_of_nodes())
        curr_weight   = evaluate(graph, curr_solution)

        for _ in range(iterations):

            (weight, solution) = select_neighbour(graph, curr_solution, curr_weight)
            if weight == curr_weight:  # local optimum
                break

            if weight < curr_weight:
                curr_solution = solution
                curr_weight   = weight


        return (curr_weight, curr_solution)
    return sls_with_given_select_fn

"""
Randomized local search
"""

def randomized_local_search(iterations: int, graph: nx.Graph, probability: float, initial_solution: list = None) -> Tuple[float, int]:

    # s: current solution and its weight
    solution = initial_solution if initial_solution is not None else random_cycle(graph.number_of_nodes())
    weight   = evaluate(graph, solution)
    
    # s*: incumbent solution and its weight
    inc_solution = solution
    inc_weight   = weight

    for _ in range(iterations):
        r = random.random()

        if r <= probability:
            (weight, solution) = random_neighbour(graph, solution)
        else:
            (weight, solution) = best_neighbour(graph, solution, weight)

        if weight < inc_weight:
            inc_solution = solution
            inc_weight   = weight

    return (inc_weight, inc_solution)

if __name__ == '__main__':

    path = sys.argv[1]

    if len(sys.argv) > 2:
        iterations = int(sys.argv[2])
    else:
        iterations = 1000

    graph = parse_instance(path)

    print('Busca local simples com primeira melhora:')
    print(simple_local_search(first_better_neighbour)(iterations, graph))
    print()

    print('Busca local simples com melhor melhora:')
    print(simple_local_search(best_neighbour)(iterations, graph))
    print()

    print('Busca local randomizada:')
    print(randomized_local_search(iterations, graph, 0.5))
    print()

    print('Caminhada aleatória')
    print(random_walk(iterations, graph))
    print()

    #print('Solução ótima por força bruta:')
    #print(brute_force(graph))

    # output_image(path, graph, solution)
