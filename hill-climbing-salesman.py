# ACA 
# Using librar tsplib95
# Documentation https://tsplib95.readthedocs.io/en/stable/pages/usage.html
# 


from joblib import Parallel, delayed
import tsplib95
import random
import time

iterations = 10
branch_factor = 38
swaps = 1

filePath = "./dj38.tsp"
result_file = open("./results/"+ filePath[:-4] + "_rand_" + (("swap_" + str(swaps)) if swaps >= 0 else "shuffle") + "_" + str(branch_factor) + "_x_" +  str(iterations) + ".txt",'w')

class Solution:
    def __init__(self, num):
        self.index = num
        self.solution = []
        self.value = 0
        self.iterations = []

    def set(self, solution, value, iterations):
        self.solution = solution
        self.value = value
        self.iterations = iterations
  
    def get(self):
        return self.solution, self.value, self.iterations

def f_n(nodes, cities, n_nodes):
	dist = 0
	for i in range(n_nodes-1):
		edge = nodes[i], nodes[i+1]
		dist += cities.get_weight(*edge) # euclidean distance
	return dist

def swap_random(nodes, cities, n_nodes, i):
	temp_nodes = nodes.copy()
	swap_place = random.randint(int((i - 1) * (n_nodes / branch_factor)), int(i * (n_nodes / branch_factor) - 1))
	if swap_place == 0:
		return ([], float('inf'))
	temp_nodes[0], temp_nodes[swap_place] = temp_nodes[swap_place], temp_nodes[0]
	temp_value = f_n(temp_nodes, cities, n_nodes)
	return (temp_nodes, temp_value)

def swap_n_random(nodes, cities, n_nodes, i):
	temp_nodes = nodes.copy()
	random_idx = list(range(n_nodes))
	random.shuffle(random_idx)
	for s in range(swaps):
		temp_nodes[random_idx[0]], temp_nodes[random_idx[1]] = temp_nodes[random_idx[1]], temp_nodes[random_idx[0]]
		random_idx = random_idx[2:]
		if len(random_idx) < 4:
			random_idx = list(range(n_nodes))
			random.shuffle(random_idx)
	temp_value = f_n(temp_nodes, cities, n_nodes)
	return (temp_nodes, temp_value)

def shuffle_random(nodes, cities, n_nodes, i):
	temp_nodes = nodes.copy()
	random.shuffle(temp_nodes)
	temp_value = f_n(temp_nodes, cities, n_nodes)
	return (temp_nodes, temp_value)

def operate(nodes, cities, n_nodes):
    b_nodes = []
    b_value = 0
    function = None
    #if swaps == 0:
    #    function = swap_random
    #elif swaps > 0:
    #    function = swap_n_random
    #else:
    #    function = shuffle_random
    childrens = Parallel(n_jobs=8)(delayed(swap_n_random)(nodes, cities, n_nodes, i+1) for i in range(branch_factor))
    print(childrens)
    for c, v in childrens:
        # Best child remain
        if(b_value == 0 or v < b_value):
            b_nodes = c
            b_value = v
    return b_nodes, b_value

def operate2(nodes, cities, n_nodes):
    b_nodes = []
    b_value = 0
    for i in range(branch_factor):
        childrens = swap_n_random(nodes, cities, n_nodes, i+1)
    print(childrens)
    for c, v in childrens:
        if(b_value == 0 or v < b_value): #best child remain
            b_nodes = c
            b_value = v
    return b_nodes, b_value

def main():
    cities = tsplib95.load(filePath)
    n_nodes = len(list(cities.get_nodes()))

    solutions = []
    best_round_value = (0, 0)

    for i in range(iterations):
        nodes = list(range(1, n_nodes + 1))
        random.shuffle(nodes) #sort all nodes randomly
        value = f_n(nodes, cities, n_nodes)

        step = 0
        result = Solution(i)
        result_file.write("###########   Round: " + str(i+1) + "   ###########\n")
        start_t = time.time()
        iterations_t = []
        while(True):
            step += 1
            # Operate -> Find best children
            child_nodes, child_value = operate(nodes, cities, n_nodes)
            #print(child_nodes, child_value)
            child_nodes2, child_value2 = operate2(nodes, cities, n_nodes)
            #print(child_nodes2, child_value2)
            if step > 10:
                break


if __name__ == "__main__":
    main()