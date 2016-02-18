#!/usr/bin/env python3

import argparse
from itertools import permutations, product
import multiprocessing as mp
import time
import random

def parse_args():
	parser = argparse.ArgumentParser(description="Given a target spell level and set of die numbers," +
		" returns a way to combine those numbers (with +, -, *, and /) in a way that'll hit" +
		" the target number. Numbers game, basically.\nCan optionally roll the dice itself.")
	parser.add_argument("-a", "--all", required=False, action='store_true', default=False,
		help="Instead of stopping after finding one solution, find all. This might take a while.")
	parser.add_argument("-l", "--level", required=False, type=int,
		help="Option to enter target spell level at command line instead of at runtime.")
	parser.add_argument("-d", "--dice", required=False, type=int, nargs='+',
		help="Option to enter dice rolls at command line instead of at runtime. Cannot be used with -r.")
	parser.add_argument("-r", "--roll", required=False, type=str, 
		help="Instead of prompting for dice, roll a set of dice randomly and use that. " +
		"Assumes d6 if not specified. Cannot be used with -d.")
	args = parser.parse_args()

	if args.roll and args.dice:
		parser.error("Cannot use -d and -r options together.")
	return args

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

# it's a lot faster to use precomputed primes, and speed is of the essence
qprimes = [[3, 5, 7], [11, 13, 17], [19, 23, 29], [31, 37, 41],
	[43, 47, 53], [59, 61, 67], [71, 73, 79], [83, 89, 97], [101, 103, 107]]

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
#  single: True if we want to stop after finding just one
#  silent: True if we don't want to display the results we find
def process_multi(dice, targets, index, index_total, pc, single, silent):

	dperms = list(permutations(dice)) # use every die exactly once
	operms = list(combinations(ops, len(dice)-1)) # any combination of operations
	oplen = len(operms)

	for idp in range(len(dperms)):
		for iop in range(oplen):

			if (idp*oplen+iop)%index_total != index:
				continue # another thread has got this one

			if single and pc.value:
				return # we've found one, and one is enough when we're in single mode, so exit

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
				if not silent:
					# if in standalone mode: build and display the string of this result
					s = op[0][1].format(dp[0], dp[1])
					for i in range(2,len(dp)):
						s = op[i-1][1].format("({0})".format(s),dp[i])
					print("{0} = {1:d}".format(s, int(num)))

				# update counter: in single mode, signals other processes to stop
				pc.value = pc.value + 1

# top-level processing method
#  level: target spell level
#  dice: dice roll result
#  single: described above
def process(level, dice, single, silent):

	targets = qprimes[level-1] # get the prime 3-tuple for this level

	if not silent and not single:
		dperms = list(permutations(dice))
		operms = list(combinations(ops, len(dice)-1))
		print()
		#print("len(operms) = {}".format(len(operms)))
		#print("len(dperms) = {}".format(len(dperms)))

		print("Targets: {0}".format(", ".join(map(str, targets))))
		print("Iterating through {0} permutations\n".format(len(dperms)*len(operms)))

	pc = mp.Value('i')
	pc.value = 0

	num_proc = mp.cpu_count() # total number of processes to spawn
	processes = []
	for i in range(num_proc):
		processes.append(mp.Process(target=process_multi, args=(dice, targets, i, num_proc, pc, single, silent)))
		processes[-1].start()

	while any([process.is_alive() for process in processes]):
		if not single:
			time.sleep(1)
		else:
			time.sleep(0.1)
		if single and pc.value:
			break

	if not silent and not single:
		print("\nWorking combinations: {0}".format(pc.value))
	elif pc.value == 0:
		print("\nNo combinations found")

	return pc.value != 0 # True if something was found, otherwise False

# Run only in standalone mode
# Prompts for spell level and dice roll results
# Note: you have to 
def main():
	print()

	args = parse_args()

	if args.level:
		level = args.level
		print("Target level {0}: targets {1}\n".format(level, qprimes[level-1]))
	else:
		level = int(input("Spell level? > "))
		print("Targets: {0}\n".format(qprimes[level-1]))

	if args.dice:
		dice = args.dice
	else:
		if args.roll:
			roll = args.roll.split('d')
			if len(roll) == 2:
				d = int(roll[1])
			else:
				d = 6
			n = int(roll[0])
			dice = [random.randint(1,d) for i in range(n)]
			print("Rolled {0}d{1}: got {2}".format(n, d, dice))
		else:
			dice = list(map(int, input("Dice? > ").split(' ')))

	single = not args.all

	process(level, dice, single=single, silent=False)

if __name__ == '__main__':
	main()