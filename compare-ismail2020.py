# 10 runs, each of 3000 iterations

# TODO take a file name as argument, output JSON representation of 'stats' to it.

from calendar import c
from criterion import *
from common import *
from local_search import *
from construction import *

RLS_PROBABILITY = 0.4
ALPHA = 0.1
RUNS = 10

criterion_thunk = lambda: IterationCriterion(3000)

instances = {
    'kroA100': 'instances/kroA100.tsp',
    'kroA150': 'instances/kroA150.tsp',
    'kroB100': 'instances/kroB100.tsp',
    'kroB150': 'instances/kroB150.tsp',
    'kroC100': 'instances/kroC100.tsp',
    'kroD100': 'instances/kroD100.tsp',
    'kroE100': 'instances/kroE100.tsp',
};

graphs = {}
for (name, path) in instances.items():
    graphs[name] = parse_instance(path)

# TODO some algorithms are missing

algos = {
    'RAND': lambda graph: random_walk(graph, criterion_thunk),
    'RLS': lambda graph: randomized_local_search(graph, RLS_PROBABILITY, criterion_thunk),
    'RGA': lambda graph: repeated_greedy_alpha(graph, ALPHA, criterion_thunk)
}

stats = {}
for instance in instances:
    stats[instance] = {}
    for algo in algos:
        stats[instance][algo] = {}
        stats[instance][algo]['runs'] = {}

for run in range(RUNS):
    print('Run', run)
    for (name, graph) in graphs.items():
        print('  ', name)
        for algo in algos:
            print('    ', algo)
            (weight, sol) = algos[algo](graph)
            stats[name][algo]['runs'][run] = weight

for instance in stats:
    for algo in stats[instance]:
        best  = float('inf')
        worst = float('-inf')
        avg   = 0
        for run in stats[instance][algo]['runs']:
            weight = stats[instance][algo]['runs'][run]
            if weight < best:
                best = weight
            if weight > worst:
                worst = weight
            avg += weight
        avg /= RUNS

        stats[instance][algo]['best'] = best
        stats[instance][algo]['worst'] = worst
        stats[instance][algo]['avg'] = avg

print(stats)


