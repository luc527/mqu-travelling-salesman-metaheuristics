import tsplib95 as tsplib
import sys

def square_matrix(n, x=None):
    m = [[] for _ in range(n)]
    for i in range(n):
        m[i] = [x for _ in range(n)]
    return m

def print_matrix(m):
    for i in range(0, len(m)):
        for j in range(0, len(m[i])):
            print(m[i][j], end='\t')
        print()

def parse_instance(filename):
    problem = tsplib.load(filename)
    return problem.edge_weights

distmatrix = parse_instance(sys.argv[1])

print_matrix(distmatrix)

# let's get instances from http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/
