# ACA 
# Using librar tsplib95
# Documentation https://tsplib95.readthedocs.io/en/stable/pages/usage.html
# 


from joblib import Parallel, delayed
import tsplib95
import random
import time

iterations = 10
branch_factor = 194
swaps = 2

filePath = "./qa194.tsp"#"./dj38.tsp"
result_file = open("./results/"+ filePath[:-4] + "swaps_2_results.txt",'w')

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

def evaluation_function(nodes, cities, n_nodes):
	dist = 0
	for i in range(n_nodes-1):
		edge = nodes[i], nodes[i+1]
		dist += cities.get_weight(*edge) # euclidean distance
	return dist

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
	temp_value = evaluation_function(temp_nodes, cities, n_nodes)
	return (temp_nodes, temp_value)

def operate(nodes, cities, n_nodes):
    b_nodes = []
    childrens = []
    b_value = 0
    for i in range(branch_factor):
        childrens.append(swap_n_random(nodes, cities, n_nodes, i+1))
    for c, v in childrens:
        if(b_value == 0 or v < b_value): #keep only the best
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
        value = evaluation_function(nodes, cities, n_nodes)

        step = 0
        result = Solution(i)
        result_file.write("\t==============  Round: " + str(i+1) + "   ==============\n")
        start_t = time.time()
        iterations_t = []
        while(True):
            step += 1
            # Operate -> Find best children
            child_nodes, child_value = operate(nodes, cities, n_nodes)
            result_file.write("\t==== "+ str(step) + " iteration -> f(n): " + str(value) + "\n")# Success reduces distance value?
            if child_value <= value and step <= 300:
                value = child_value
                nodes = child_nodes
            else:
                result.set(nodes, value, step)
                solutions.append(result)
                result_file.write("\n\t====   Best Solution -> " + str(step) + " iterations: f(n): " + str(value))
                result_file.write("\n\t====    - Elapsed time: " + str(sum(iterations_t)) + " |  time / iterations: " + str(sum(iterations_t)/step) + "\n\n\n")
                if best_round_value[0] == 0 or value < best_round_value[0]:
                    best_round_value = (value, i+1)
                    with open(result_file.name[:-4] + "_nodes.txt",'w',encoding = 'utf-8') as f:
                        f.write("\t=====  Best Solution found, in round: " + str(i+1) + "  -> f(n): " + str(best_round_value[0]) + "   ######\n")
                        f.write("\t=====      - Elapsed time: " + str(sum(iterations_t)) + " |  time / iterations: " + str(sum(iterations_t)/step) + "\n")
                        f.write("Order to visit cities: ")
                        for n in nodes:
                            f.write(str(n) + ", ")
                    if i == step-1:
                        result_file.write("Best Solution: " + str(best_round_value[1]) + " round -> f(n): " + str(best_round_value[0]))
                break
            iterations_t.append(time.time() - start_t)
            start_t = time.time()
    result_file.close()

if __name__ == "__main__":
    main()