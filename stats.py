# TODO take a file name as argument, output JSON representation of 'stats' to it.

# TODO make parameters configurable
# - rls probability
# - alpha
# - number of runs
# - iterations for each run

from calendar import c
from criterion import *
from common import *
from local_search import *
from construction import *
from pprint import pprint
import argparse as argp


# 'n' is the problem size (number of nodes)
# 'bks' is the best known solution

instances = {
    'a280':     { 'n': 280, 'path': 'instances/a280.tsp',     'bks':   2579 },
    'att48':    { 'n':  48, 'path': 'instances/att48.tsp',    'bks':  10628 },
    'bayg29':   { 'n':  29, 'path': 'instances/bayg29.tsp',   'bks':   1610 },
    'bays29':   { 'n':  29, 'path': 'instances/bays29.tsp',   'bks':   2020 },
    'berlin52': { 'n':  52, 'path': 'instances/berlin52.tsp', 'bks':   7542 },
    'bier127':  { 'n': 127, 'path': 'instances/bier127.tsp',  'bks': 118282 },
    'brazil58': { 'n':  58, 'path': 'instances/brazil58.tsp', 'bks':  25395 },
    'eli51':    { 'n':  51, 'path': 'instances/eil51.tsp',    'bks':    426 },
    'eli76':    { 'n':  76, 'path': 'instances/eil76.tsp',    'bks':    538 },
    'eli101':   { 'n': 101, 'path': 'instances/eil101.tsp',   'bks':    629 },
    'kroA100':  { 'n': 100, 'path': 'instances/kroA100.tsp',  'bks':  21282 },
    'kroA150':  { 'n': 150, 'path': 'instances/kroA150.tsp',  'bks':  26524 },
    'kroB100':  { 'n': 100, 'path': 'instances/kroB100.tsp',  'bks':  22141 },
    'kroB150':  { 'n': 150, 'path': 'instances/kroB150.tsp',  'bks':  26130 },
    'kroC100':  { 'n': 100, 'path': 'instances/kroC100.tsp',  'bks':  20749 },
    'kroD100':  { 'n': 100, 'path': 'instances/kroD100.tsp',  'bks':  21294 },
    'kroE100':  { 'n': 100, 'path': 'instances/kroE100.tsp',  'bks':  22068 },
    'pr76':     { 'n':  76, 'path': 'instances/pr76.tsp',     'bks': 108159 },
    'st70':     { 'n':  70, 'path': 'instances/st70.tsp',     'bks':    675 },
}


# TODO some algorithms are missing

algos = {
    'RAND': { 'name': 'Random walk'},
    'RLS': { 'name': 'Randomized local search'},
    'RGA': { 'name': 'Repeated greedy-alpha'}
}
# Later each entry will also have a 'fn' entry with the function that implements the algorithm
# So when adding algorithms here don't forget to also add them there

instances_str = '\n' + '\n'.join(map(lambda s: '  ' + s, instances.keys()))
algos_str = '\n' + '\n'.join(map(lambda s: '  ' + s + ' (' + algos[s]['name'] + ')', algos.keys()))

description_str = f'Instances: {instances_str}\n\nAlgorithms: {algos_str}'

parser = argp.ArgumentParser(description=description_str, formatter_class=argp.RawDescriptionHelpFormatter)

parser.add_argument('--runs', type=int, default=10)
parser.add_argument('--rlsprob', type=float, default=0.4, help='The probability of taking a random neighbour in the randomized local search')
parser.add_argument('--alpha', type=float, default=0.1, help='The alpha for greedy-alpha')
parser.add_argument('--criterion', type=str, default='iters,3000', help='The stop criterion for each algorithm; options: iters,N for N iterations or time,N for N seconds')
parser.add_argument('--algos', type=str, help='Which algorithms to run, separated by comma (no spaces!), or \'all\' to run all of them (example: RAND,RGA)', default='all')
parser.add_argument('--instances', type=str, help='Which instances to run, separated by comma (no spaces!), or \'all\' to run all of them (example: brazil58,bier127,pr76)', default='all')

args = parser.parse_args()

if args.runs < 1 or args.runs > 100:
    print('--runs must be in [1, 100]')
    quit()

if args.rlsprob < 0 or args.rlsprob > 1:
    print('--rlsprob must be in (0, 1]')
    quit()

if args.alpha < 0 or args.alpha > 1:
    print('--alpha must be in (0, 1]')
    quit()

crit_toks = args.criterion.split(',')
if len(crit_toks) != 2:
    print('Malformed --criterion')
    quit()

[crit, crit_N] = crit_toks
crit_N = int(crit_N)
if crit == 'time':
    make_criterion = lambda: TimeCriterion(crit_N)
elif crit == 'iters':
    make_criterion = lambda: IterationCriterion(crit_N)
else:
    print(f'Malformed criterion {crit}')
    quit()

RLS_PROBABILITY = args.rlsprob
ALPHA           = args.alpha
RUNS            = args.runs

algos['RAND']['fn'] = lambda graph: random_walk(graph, make_criterion)
algos['RLS']['fn'] = lambda graph: randomized_local_search(graph, RLS_PROBABILITY, make_criterion)
algos['RGA']['fn'] = lambda graph: repeated_greedy(graph, lambda graph: greedy_alpha(graph, ALPHA), make_criterion)


algos_to_run = algos.keys()
if args.algos != 'all':
    algos_to_run = args.algos.split(',')

for algo in list(algos.keys()):
    if algo not in algos_to_run:
        del algos[algo]

instances_to_run = instances.keys()
if args.instances != 'all':
    instances_to_run = args.instances.split(',')

for instance in list(instances.keys()):
    if instance not in instances_to_run:
        del instances[instance]

print('Parsing instances...')

graphs = {}
for name in instances:
    print(f'    Parsing {name}...')
    graphs[name] = parse_instance(instances[name]['path'])
print()

stats = {}
for instance in instances:
    stats[instance] = {}
    stats[instance]['algos'] = {}
    for algo in algos:
        stats[instance]['algos'][algo] = {}
        stats[instance]['algos'][algo]['runs'] = [-1 for _ in range(RUNS)]

for run in range(RUNS):
    for (name, graph) in graphs.items():
        print('Run', run, name)
        for algo in algos:
            print('    ', algo)
            (weight, sol) = algos[algo]['fn'](graph)
            stats[name]['algos'][algo]['runs'][run] = weight
    print()

for instance in stats:
    bks = instances[instance]['bks']
    stats[instance]['bks'] = bks

    for algo in stats[instance]['algos']:
        best  = float('inf')
        worst = float('-inf')
        avg   = 0

        for weight in stats[instance]['algos'][algo]['runs']:
            if weight < best:
                best = weight
            if weight > worst:
                worst = weight
            avg += weight
        avg /= RUNS

        stats[instance]['algos'][algo]['best'] = best
        stats[instance]['algos'][algo]['worst'] = worst
        stats[instance]['algos'][algo]['avg'] = avg

        stats[instance]['algos'][algo]['Dbest%'] = ((best - bks) / bks) * 100
        stats[instance]['algos'][algo]['Davg%'] = ((avg - bks) / bks) * 100

pprint(stats)