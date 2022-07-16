from criterion import *
from common import *
from local_search import *
from construction import *
from pprint import pprint
import argparse as argp
import json


# 'n' is the problem size (number of nodes)
# 'bks' is the best known solution

instances = {
    'a280':     { 'n':  280, 'path': 'instances/a280.tsp',     'bks':   2579 },
    'att48':    { 'n':   48, 'path': 'instances/att48.tsp',    'bks':  10628 },
    'bayg29':   { 'n':   29, 'path': 'instances/bayg29.tsp',   'bks':   1610 },
    'bays29':   { 'n':   29, 'path': 'instances/bays29.tsp',   'bks':   2020 },
    'berlin52': { 'n':   52, 'path': 'instances/berlin52.tsp', 'bks':   7542 },
    'bier127':  { 'n':  127, 'path': 'instances/bier127.tsp',  'bks': 118282 },
    'brazil58': { 'n':   58, 'path': 'instances/brazil58.tsp', 'bks':  25395 },
    'd1655':    { 'n': 1655, 'path': 'instances/d1655.tsp',    'bks':  62128 },
    'eli51':    { 'n':   51, 'path': 'instances/eil51.tsp',    'bks':    426 },
    'eli76':    { 'n':   76, 'path': 'instances/eil76.tsp',    'bks':    538 },
    'eli101':   { 'n':  101, 'path': 'instances/eil101.tsp',   'bks':    629 },
    'kroA100':  { 'n':  100, 'path': 'instances/kroA100.tsp',  'bks':  21282 },
    'kroA150':  { 'n':  150, 'path': 'instances/kroA150.tsp',  'bks':  26524 },
    'kroB100':  { 'n':  100, 'path': 'instances/kroB100.tsp',  'bks':  22141 },
    'kroB150':  { 'n':  150, 'path': 'instances/kroB150.tsp',  'bks':  26130 },
    'kroC100':  { 'n':  100, 'path': 'instances/kroC100.tsp',  'bks':  20749 },
    'kroD100':  { 'n':  100, 'path': 'instances/kroD100.tsp',  'bks':  21294 },
    'kroE100':  { 'n':  100, 'path': 'instances/kroE100.tsp',  'bks':  22068 },
    'pr76':     { 'n':   76, 'path': 'instances/pr76.tsp',     'bks': 108159 },
    'st70':     { 'n':   70, 'path': 'instances/st70.tsp',     'bks':    675 },
}


# TODO some algorithms are missing

algos = {
    'RAND': { 'name': 'Random walk' },
    'RLS': { 'name': 'Randomized local search (random initial solution)' },
    'RGA': { 'name': 'Repeated greedy-alpha' },
    'RLSG': { 'name': 'Randomized local search (greedy initial solution)' },
    'ILSRR': { 'name': 'Iterated local search (with randomized local search and random initial solution) '},
    'ILSRG': { 'name': 'Iterated local search (with randomized local search and greedy initial solution) '}
}
# Later each entry will also have a 'fn' entry with the function that implements the algorithm
# So when adding algorithms here don't forget to also add them there too

instances_str = '\n' + '\n'.join(map(lambda s: '  ' + s, instances.keys()))
algos_str = '\n' + '\n'.join(map(lambda s: '  ' + s + ' (' + algos[s]['name'] + ')', algos.keys()))

description_str = f'Instances: {instances_str}\n\nAlgorithms: {algos_str}'

parser = argp.ArgumentParser(description=description_str, formatter_class=argp.RawDescriptionHelpFormatter)

parser.add_argument('--runs', type=int, default=10, help='Default 10')

parser.add_argument('--rlsprob', type=float, default=0.4,\
    help='The probability of taking a random neighbour in the randomized local search (default 0.4)')

parser.add_argument('--ilsperc', type=float, default=0.1,\
    help='The percentage of a perturbance at each iteration of the iterated local search (default 0.1)')

parser.add_argument('--alpha', type=float, default=0.1,\
    help='The alpha for greedy-alpha (default 0.1)')

parser.add_argument('--criterion', type=str, default='iters,3000',\
    help='The stop criterion for each algorithm; options: iters,N for N iterations, time,N for N seconds or seen,N for N times seen the best solution so far (default iters,3000)')

parser.add_argument('--subcriterion', type=str, default='iters,1000',\
    help='Some algorithms use other algorithms at each iteration (e.g. GRASP does a local search at each iteration), so you can use this parameter to set the criterion for these sub-algorithms (default: iters,100)')

parser.add_argument('--supercriterion', type=str,\
    help='Stop criterion for the outer loop of algorithms like GRASP and ILS in which each iteration is itself another algorithm (the idea is to allow for something like --criterion iters,3000 --supercriterion iters,30 --subcriterion iters,100 if you don\'t want those algorithms to take too long) (if not informed, takes the same value as --criterion)')

parser.add_argument('--algos', type=str, default='all',\
    help='Which algorithms to run, separated by comma (no spaces!), or \'all\' to run all of them (example: RAND,RGA) (default all)')

parser.add_argument('--instances', type=str, default='all',\
    help='Which instances to run, separated by comma (no spaces!), or \'all\' to run all of them (example: brazil58,bier127,pr76) (default all)')

parser.add_argument('--out', type=str, help='Output the generated statistics as JSON to this file')

args = parser.parse_args()

if args.runs < 1 or args.runs > 100:
    print('--runs must be in [1, 100]')
    quit()

if args.rlsprob < 0 or args.rlsprob > 1:
    print('--rlsprob must be in [0, 1]')
    quit()

if args.alpha < 0 or args.alpha > 1:
    print('--alpha must be in [0, 1]')
    quit()

if args.ilsperc < 0 or args.ilsperc > 1:
    print('--ilsperc must be in [0, 1]')
    quit()

def criterion_from_arg(criterion_string):
    toks = criterion_string.split(',')
    if len(toks) != 2:
        print('Malformed criterion argument ' + criterion_string)
        quit()
    [crit, n] = toks
    n = int(n)
    if crit == 'time':
        mk = lambda: TimeCriterion(n)
    elif crit == 'iters':
        mk = lambda: IterationCriterion(n)
    elif crit == 'seen':
        mk = lambda: TimesSeenBestCriterion(n)
    else:
        print(f'Unknown criterion {crit}')
        quit()

    return mk

make_criterion = criterion_from_arg(args.criterion)
make_supercriterion = make_criterion if args.supercriterion is None else criterion_from_arg(args.supercriterion)
make_subcriterion = criterion_from_arg(args.subcriterion)

RLS_PROBABILITY      = args.rlsprob
ALPHA                = args.alpha
RUNS                 = args.runs
ILS_PERTURBANCE_PERC = args.ilsperc

algos['RAND']['fn'] = lambda graph: random_walk(graph, make_criterion)
algos['RLS']['fn'] = lambda graph: randomized_local_search(graph, RLS_PROBABILITY, make_criterion)
algos['RGA']['fn'] = lambda graph: repeated_greedy(graph, lambda graph: greedy_alpha(graph, ALPHA), make_criterion)
algos['RLSG']['fn'] = lambda graph: randomized_local_search(graph, RLS_PROBABILITY, make_criterion, greedy(graph)[1])
algos['ILSRR']['fn'] = lambda graph: iterated_local_search(\
    graph,\
    lambda graph, initial: randomized_local_search(graph, RLS_PROBABILITY, make_subcriterion, initial),\
    make_supercriterion,\
    ILS_PERTURBANCE_PERC\
)
algos['ILSRG']['fn'] = lambda graph: iterated_local_search(\
    graph,\
    lambda graph, initial: randomized_local_search(graph, RLS_PROBABILITY, make_subcriterion, initial),\
    make_supercriterion,\
    ILS_PERTURBANCE_PERC,\
    greedy(graph)[1]\
)

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

outpath = args.out

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

    stats[instance]['greedy'] = greedy(graphs[instance])[0]

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

if outpath is not None:
    with open(outpath, 'w') as outfile:
        output = json.dumps(stats, indent=4, sort_keys=True)
        outfile.write(output)
        print('Dumped JSON to ' + outpath)