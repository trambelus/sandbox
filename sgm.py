#!/usr/bin/env python

import random
from threading import Thread
from sg import process
import sqlite3
from pprint import pprint

MIN_DICE = 2
MAX_DICE = 8

MAX_DIE = 6

def wait(stop):
	#if input() == 'q':
		stop[0] = True

def init_db():
	db = sqlite3.connect('sgm.db3')
	db.execute("""CREATE TABLE IF NOT EXISTS d6 (
		id TEXT PRIMARY KEY UNIQUE,
		result DOUBLE,
		num_tests INT
	);""")
	db.commit()
	db.close()

def save(results):
	db = sqlite3.connect('sgm.db3')
	for level in range(len(results)):
		for num_dice in range(len(results[0])):
			db.execute("REPLACE INTO d6 (id, result, num_tests) VALUES (?,?,?)",
				("{};{}".format(level+1, num_dice+MIN_DICE), results[level][num_dice][0], results[level][num_dice][1]))

	db.commit()
	db.close()

def roll(n,d):
	return [random.randint(1,d) for i in range(n)]

def main():
	stop = [False]
	Thread(target=wait, args=(stop,)).start()
	results = [[[0.0, 0] for i in range(MIN_DICE, MAX_DICE+1)] for j in range(1, 10)] # results[level][num_dice]

	init_db()
	#results = init_db()

	#while not stop[0]:
	while True:
		for level in range(1, 10):
			#print("level = {}".format(level))
			for num_dice in range(MIN_DICE, MAX_DICE+1):
				#print("num_dice = {}".format(num_dice))
				dice = roll(num_dice, MAX_DIE)
				res = process(level, dice, single=True, silent=True)

				#print(results)
				current = results[level-1][num_dice-MIN_DICE][0]
				num_tests = results[level-1][num_dice-MIN_DICE][1]

				if num_tests == 0:
					results[level-1][num_dice-MIN_DICE] = [100*float(res), 1]
				else:
					results[level-1][num_dice-MIN_DICE][0] = (num_tests*current + 100*float(res)) / (num_tests + 1)
					results[level-1][num_dice-MIN_DICE][1] = num_tests + 1

		pprint(results)
		save(results)

if __name__ == '__main__':
	main()