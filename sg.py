#!/usr/bin/env python3

from itertools import permutations, product
import multiprocessing as mp
import time

def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(range(n), repeat=r):
            yield tuple(pool[i] for i in indices)

ops = [
	[lambda x,y: x+y, "{0} + {1}"],
	[lambda x,y: x-y, "{0} - {1}"],
	[lambda x,y: y-x, "{1} - {0}"],
	[lambda x,y: x*y, "{0} * {1}"],
	[lambda x,y: x/y, "{0} / {1}"],
	[lambda x,y: y/x, "{1} / {0}"],
]

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

def process_multi(dice, targets, index, index_total, pc, quick, stopped):
	ops = [
		[lambda x,y: x+y, "{0} + {1}"],
		[lambda x,y: x-y, "{0} - {1}"],
		[lambda x,y: y-x, "{1} - {0}"],
		[lambda x,y: x*y, "{0} * {1}"],
		[lambda x,y: x/y, "{0} / {1}"],
		[lambda x,y: y/x, "{1} / {0}"],
	]

	dperms = list(permutations(dice))
	operms = list(combinations(ops, len(dice)-1))
	oplen = len(operms)

	for idp in range(len(dperms)):
		for iop in range(oplen):

			if (idp*oplen+iop)%index_total != index:
				continue

			if stopped.value:
				return

			dp = dperms[idp]
			op = operms[iop]
			try:
				num = op[0][0](dp[0],dp[1])
				for i in range(2, len(dp)):
					num = op[i-1][0](num,dp[i])
			except ZeroDivisionError:
				continue
			if num in targets:
				s = op[0][1].format(dp[0], dp[1])
				for i in range(2,len(dp)):
					s = op[i-1][1].format("({0})".format(s),dp[i])
				if not quick:
					print("{0} = {1:d}".format(s, int(num)))
				pc.value = pc.value + 1

def process(level, dice, quick=False):

	targets = primes(level)
	dperms = list(permutations(dice))
	operms = list(combinations(ops, len(dice)-1))

	if not quick:
		print("len(operms) = {}".format(len(operms)))
		print()
		print("len(dperms) = {}".format(len(dperms)))

		print("Targets: {0}".format(", ".join(map(str, targets))))
		print("Iterating through {0} permutations\n".format(len(dperms)*len(operms)))

	pc = mp.Value('i')
	pc.value = 0
	stopped = mp.Value('b')
	stopped.value = 0

	num_proc = mp.cpu_count()
	processes = []
	for i in range(num_proc):
		processes.append(mp.Process(target=process_multi, args=(dice, targets, i, num_proc, pc, quick, stopped)))
		processes[-1].start()

	while any([process.is_alive() for process in processes]):
		if not quick:
			time.sleep(1)
		if quick and pc.value != 0:
			stopped.value = 1

	if not quick:
		print("\nWorking combinations: {0}".format(pc.value))

	return pc.value != 0


def main():
	print()
	level = int(input("Spell level? > "))
	dice = list(map(int, input("Dice? > ").split(' ')))

	print(process(level, dice, quick=False))

if __name__ == '__main__':
	main()