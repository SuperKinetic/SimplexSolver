from Simplex import SimplexSolver as Solver
from fractions import Fraction

matrix = [
	['1', '-1', '-2', '-1',  '0',  '0',  '0',   '0'],
	['0',  '2',  '1',  '5',  '1',  '0',  '0',  '90'],
	['0',  '4',  '3',  '0',  '0',  '1',  '0',  '72'],
	['0',  '3',  '1',  '2',  '0',  '0',  '1', '100']
]

matrix = [[Fraction(x) for x in row] for row in matrix]

s = Solver(matrix, variables=['x', 'y', 'z'], slack_variables=['s1', 's2', 's3'])

print(s.dumps() + '\n')

s.solve()

print(s.dumps() + '\n')
print(s.get_solution())