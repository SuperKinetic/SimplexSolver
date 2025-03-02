from fractions import Fraction
import math

class SimplexSolver():
	__table = None
	__columns = None
	__rows = None
	__maximise_row = None
	__P_col = None
	__value_col = None
	__header = None
	__side = None
	__variables = None
	__slack_variables = None


	def check_setup(self, table, variables, slack_variables):
		# check if table has rows
		if type(table) is not list:
			raise Exception(f'the table must be a list')

		# check if the table has columns
		for row in table:
			if type(row) is not list:
				raise Exception(f'every row in the table must be another list')
			
		# check if the table is rectangular
		if not all(len(i) == len(table[0]) for i in table):
			raise Exception(f'table must be rectangular')
		
		# check if every element in the table is a fraction
		for row in table:
			for element in row:
				if type(element) is not Fraction:
					raise Exception(f'every sub-element in the table must be a fraction')
				
				
		# the rows must have a length of slack_variables + 1, 1 for the P row
		if len(slack_variables) + 1 != len(table):
			raise Exception('{{slack_variables + 1}} must be equal to the rows in the table')
		
		# the columns must have a length of variables + slack variables + 2, 1 for the P column and value column 
		if len(variables) + len(slack_variables) + 2 != len(table[0]):
			raise Exception('{{variables + slack_variables + 2}} must be equal to the columns in the table')
		
		# the type of all variables must be a list
		if type(variables) is not list or type(slack_variables) is not list:
			raise Exception('variables/slack_variables must be a list')
		
		# every element in variables must be a string
		for element in variables:
			if type(element) is not str:
				raise Exception(f'every element in variables must be a string')
			
		# every element in slack_variables must be string
		for element in slack_variables:
			if type(element) is not str:
				raise Exception(f'every element in slack_variables must be a string')
			
		for row in range(len(table)):
			for col in range(len(table[0])):
				if row != 0: # ignore maximise row
					if table[row][col] < 0:
						raise Exception(f'cannot have negative values outside of the maximise row at ({row}, {col})')
		

	def __init__(self, table, variables, slack_variables, skip_checks = False):
		if not skip_checks: 
			self.check_setup(table, variables, slack_variables)

		# setup rows and columns
		self.__rows = len(table)
		self.__columns = len(table[0])

		# setup row data
		self.__maximise_row = 0
		self.__P_col = 0
		self.__value_col = len(table[0]) - 1

		# setup variable data
		self.__variables = variables
		self.__slack_variables = slack_variables
		
		# setup header and side data for solution
		self.__header = ['P'] + self.__variables + self.__slack_variables + ['val']
		self.__side = ['P'] + self.__slack_variables

		# set table
		self.__table = table

	# gets a certain row
	def __get_row(self, row: int) -> list:
		return self.__table[row]
	
	# sets the row
	def __set_row(self, row: int, new_row: list) -> None:
		self.__table[row] = new_row

	# returns the sum of 2 rows
	def __add_two_rows(self, row1: list, row2: list) -> list:
		resultant_list = [None] * self.__columns
		for i in range(self.__columns):
			resultant_list[i] = row1[i] + row2[i]
		return resultant_list

	# multiplies a row by a fraction
	def __multiply_row_by_fraction(self, row: list, constant: Fraction) -> list:
		resultant_list = [None] * self.__columns
		for i in range(self.__columns):
			resultant_list[i] = row[i] * constant
		return resultant_list

	# multiplies row by a fraction and saves to that row
	def __row_op_multiply(self, row: int, constant: Fraction):
		buffer_row = self.__get_row(row)

		resultant_row = self.__multiply_row_by_fraction(buffer_row, constant)

		self.__set_row(row, resultant_row)

		return self

	# multiplies a row by a constant and adds that row to another row and saves to other row
	def __row_op_multiply_and_add(self, row1: int, constant: Fraction, row2: int):
		buffer_row1 = self.__get_row(row1)
		buffer_row2 = self.__get_row(row2)

		resultant_row = self.__multiply_row_by_fraction(buffer_row1, constant)
		resultant_row = self.__add_two_rows(resultant_row, buffer_row2)

		self.__set_row(row2, resultant_row)

		return self

	# check if the solution is optimal where every element in the maximise rowis non-negative
	def is_optimal(self):
		optimal = True
		buffer_row = self.__get_row(self.__maximise_row)
		
		for i in range(self.__columns):
			if buffer_row[i] < 0:
				optimal = False
				break
		
		return optimal

	# gets the pivot column by checking the most negative number in the maximise row
	def __get_pivot_column(self):
		buffer_row = self.__get_row(self.__maximise_row)

		min_element = min(self.__table[self.__maximise_row])

		# pivot does not exist if the element is greater than 0 despite being the smalles
		if min_element < 0:
			index = buffer_row.index(min_element)
		else:
			index = -1

		return index
	
	# gets the pivot
	def __get_pivot(self):
		if self.is_optimal():
			return (-1, -1)
		
		# pivot column provided in a separate method
		pivot_col = self.__get_pivot_column()
		divisions = []

		# performing ratio test
		for i in range(self.__rows):
			if i == self.__maximise_row:
				continue

			# although none of these elements should be negative, if they are they should be considered as
			#  a value of infinity
			#
			# add the ratio of the result to divisions
			if self.__get_row(i)[pivot_col] <= 0:
				divisions.append(math.inf)
			else:
				divisions.append(self.__get_row(i)[self.__value_col] / self.__get_row(i)[pivot_col])
		
		# find the index of the min element which should correspond the location in the table
		min_element = min(divisions)
		pivot_row = divisions.index(min_element) + 1

		return (pivot_row, pivot_col)

	def solve(self):
		# iterate while the table is not optimal
		while not self.is_optimal():
			self.__step()

	def solve_by_step(self):
		# iterate while the table is not optimal
		while not self.is_optimal():
			yield self.__step()

	def __step(self) -> bool:
		if not self.is_optimal():
			# save the pivot row and column
			pivot_row, pivot_col = self.__get_pivot()

			# get the pivot element and multiply the pivot row by the reciprocal of the fraction
			#  this ensures that the same element becomes 1
			pivot_element = self.__get_row(pivot_row)[pivot_col]
			self.__row_op_multiply(pivot_row, pivot_element ** -1)

			# iterate through every row again
			for i in range(self.__rows):
				# ignore the pivot row
				if i != pivot_row:
					# find the factor that you need to multiply by so that once added the element in the pivot_row
					#  at that row becomes 0
					factor = -(self.__table[i][pivot_col])
					self.__row_op_multiply_and_add(pivot_row, factor, i)

					# since there is a swap, the side at that row now bomes the header at that col
					self.__side[pivot_row] = self.__header[pivot_col]

					return False

			return True


	def get_solution(self):
		# get the P text the user has provided because it may not be 'P'
		P_text = self.__header[self.__P_col]
		P_val = str(self.__get_row(self.__maximise_row)[self.__value_col])
		
		# initialise solution dictionary
		solution = {P_text: P_val}

		# iterate through rows
		for i in range(self.__rows):
			# ignore maximise row and check if the side is in variables because that means the solution to that variable is not 0
			if i != self.__maximise_row and self.__side[i] in self.__variables:
				# set the solution
				solution[self.__side[i]] = str(self.__get_row(i)[self.__value_col])

		return solution

	# dump the table in a text format
	def dumps(self):
		txt = ''

		for i in range(len(self.__table)):
			txt += f'{self.__side[i]}: ' + ', '.join([str(x) for x in self.__table[i]]) + '\n'
		
		return txt.removesuffix('\n')
	

def main():
	matrix = [
		['1', '-1', '-2', '-1',  '0',  '0',  '0',   '0'],
		['0',  '2',  '1',  '5',  '1',  '0',  '0',  '90'],
		['0',  '4',  '3',  '0',  '0',  '1',  '0',  '72'],
		['0',  '3',  '1',  '2',  '0',  '0',  '1', '100']
	]
	
	# set every element to a fraction
	matrix = [[Fraction(x) for x in row] for row in matrix]

	s = SimplexSolver(matrix, variables=['x', 'y', 'z'], slack_variables=['s1', 's2', 's3'])
	print(s.dumps() + '\n')

	s.solve()

	print(s.dumps() + '\n')
	print(s.get_solution())

if __name__ == '__main__':
	main()