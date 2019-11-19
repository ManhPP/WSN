from __future__ import print_function
from ortools.sat.python import cp_model
import time
import numpy as np
from itertools import combinations
def sub_lists(my_list):
	subs = []
	for i in range(0, len(my_list)+1):
	    temp = [list(x) for x in combinations(my_list, i)]
	    if len(temp) > 0:
	        subs.extend(temp)
	result = []
	for i in subs:
		if len(i) > 1:
			result.append(i)
	return result

if __name__ == '__main__':
	# l = [11,13]
	# for i in range(len(l) - 1):
	# 	for j in range(i+1, len(l)):
	# 		print((l[i],l[j]))
	# 		print((l[j],l[i]))
	print(sub_lists([1,2,3,4]))