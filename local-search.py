import sys
from common import * 

def neighborhood(solution):
    n = len(solution)
    neighborhood = []
    for i in range(n):
        j = (i + 1) % n
        nb = list(solution)
        nb[i], nb[j] = nb[j], nb[i]
        neighborhood.append(nb)
    return neighborhood


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

"""
Simple local search
"""

# TODO make simple_local_search take a strategy and *return a function* that uses that strategy

def simple_local_search(graph: nx.Graph, select_fn) -> Tuple[float, list]:
    global iterations

    curr_solution = random_cycle(graph.number_of_nodes())
    curr_weight   = evaluate(graph, curr_solution)

    for _ in range(iterations):
        (weight, solution) = select_fn(graph, curr_solution, curr_weight)
        if weight < curr_weight:
            curr_solution = solution
            curr_weight   = weight

    return (curr_weight, curr_solution)

def simple_local_search(select_neighbour):
    def sls_with_given_select_fn(iterations: int, graph: nx.Graph) -> Tuple[float, list]:
        curr_solution = random_cycle(graph.number_of_nodes())
        curr_weight   = evaluate(graph, curr_solution)
        for _ in range(iterations):
            (weight, solution) = select_neighbour(graph, curr_solution, curr_weight)
            if weight < curr_weight:
                curr_solution = solution
                curr_weight   = weight
        return (curr_weight, curr_solution)
    return sls_with_given_select_fn



path = sys.argv[1]

if len(sys.argv) > 2:
    iterations = int(sys.argv[2])
else:
    iterations = 65536

graph = parse_instance(path)

print('Busca local simples com primeira melhora:')
print(simple_local_search(first_better_neighbour)(iterations, graph))

print('Busca local simples com melhor melhora:')
print(simple_local_search(best_neighbour)(iterations, graph))

print('Caminhada aleatória')
print(random_walk(iterations, graph))

#print('Solução ótima por força bruta:')
#print(brute_force(graph))

# output_image(path, graph, solution)
