#!/usr/bin/env python3

# TODO: argparse, dice roll within script

from itertools import permutations, product
import multiprocessing as mp
import time

# modification of itertools combinations: unordered and with repeats
def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(range(n), repeat=r):
            yield tuple(pool[i] for i in indices)

# (index for opf, string for displaying once something's found)
# TODO: separate these and work out a more efficient way to get op combinations
ops = [
	(0, "{0} + {1}"),
	(1, "{0} - {1}"),
	(2, "{1} - {0}"),
	(3, "{0} * {1}"),
	(4, "{0} / {1}"),
	(5, "{1} / {0}"),
]

# Sieve of Eratosthenes method for calculating primes (unused, but kept because cool)
def primes(level, limit=3):
	p = [True] * 200
	p[0:2] = [False, False]
	for i in range(2,16):
		for j in range(i+1, len(p)):
			if (j%i == 0):
				p[j] = False

	primes = [x for x,y in enumerate(p) if y]
	primes = primes[1:]
	p3 = [primes[i:i+limit] for i in range(0, len(primes), limit)]
	return p3[level-1]

# it's a lot quicker to use precomputed primes, and speed is of the essence
qprimes = [[3, 5, 7], [11, 13, 17], [19, 23, 29], [31, 37, 41], [43, 47, 53], [59, 61, 67], [71, 73, 79], [83, 89, 97], [101, 103, 107]]

# operations function: defines all the possible ops
def opf(i,x,y):
	if i == 0:
		return x+y
	if i == 1:
		return x-y
	if i == 2:
		return y-x
	if i == 3:
		return x*y
	if i == 4:
		return x/y
	if i == 5:
		return y/x
	return None

# multiprocessing target function
# 	dice: list of dice roll results
#  targets: the three primes we're trying to hit
#  index: ID of this worker process
#  index_total: total number of worker processes
#  pc: interprocess counter (used to signal a hit for stopping)
#  quick: True if we're doing stats analysis and False for standalone
# (I should probably rename "quick" to "single")
def process_multi(dice, targets, index, index_total, pc, quick):

	dperms = list(permutations(dice)) # use every die exactly once
	operms = list(combinations(ops, len(dice)-1)) # any combination of operations
	oplen = len(operms)

	for idp in range(len(dperms)):
		for iop in range(oplen):

			if (idp*oplen+iop)%index_total != index:
				continue # another thread has got this one

			if quick and pc.value:
				return # we've found one, and one is enough when we're in quick mode, so exit

			dp = dperms[idp]
			op = operms[iop]
			try:
				num = opf(op[0][0],dp[0],dp[1]) # result of op on first two dice
				for i in range(2, len(dp)): # loop through remaining dice/ops
					num = opf(op[i-1][0],num,dp[i])

			except ZeroDivisionError:
				continue # our final result won't have any division by zero, so skip

			if num in targets:
				# We found it
				if not quick:
					# if in standalone mode: build and display the string of this result
					s = op[0][1].format(dp[0], dp[1])
					for i in range(2,len(dp)):
						s = op[i-1][1].format("({0})".format(s),dp[i])
					print("{0} = {1:d}".format(s, int(num)))

				# update counter: in quick mode, signals other processes to stop
				pc.value = pc.value + 1

# top-level processing method
#  level: target spell level
#  dice: dice roll result
#  quick: described above
def process(level, dice, quick=False):

	targets = qprimes[level-1] # get the prime 3-tuple for this level

	if not quick:
		dperms = list(permutations(dice))
		operms = list(combinations(ops, len(dice)-1))
		print("len(operms) = {}".format(len(operms)))
		print()
		print("len(dperms) = {}".format(len(dperms)))

		print("Targets: {0}".format(", ".join(map(str, targets))))
		print("Iterating through {0} permutations\n".format(len(dperms)*len(operms)))

	pc = mp.Value('i')
	pc.value = 0

	num_proc = mp.cpu_count() # total number of processes to spawn
	processes = []
	for i in range(num_proc):
		processes.append(mp.Process(target=process_multi, args=(dice, targets, i, num_proc, pc, quick)))
		processes[-1].start()

	while any([process.is_alive() for process in processes]):
		if not quick:
			time.sleep(1)
		else:
			time.sleep(0.1)
		if quick and pc.value:
			break

	if not quick:
		print("\nWorking combinations: {0}".format(pc.value))

	return pc.value != 0 # True if something was found, otherwise False

# Run only in standalone mode
# Prompts for spell level and dice roll results
# Note: you have to 
def main():
	print()
	level = int(input("Spell level? > "))
	dice = list(map(int, input("Dice? > ").split(' ')))

	print(process(level, dice, quick=False))

if __name__ == '__main__':
	main()