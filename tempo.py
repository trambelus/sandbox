#!/usr/bin/env python3
# tempo.py - press any key to set the tempo, and this script will display the
#  approximate tempo of the last several presses.

import argparse
import time
from msvcrt import getch
import sys

class BoundedList(list):
	"""Just like a list, but with a maximum size and an easy averager."""

	def __init__(self, size):
		self.size = size

	def push(self, item):
		"""Appends an item to the list. If it's too long, truncates."""
		self.append(item)
		ret = None

		if len(self) > self.size:
			ret = self.pop(0)

		return ret

	def average(self):
		"""Returns the average of this list's elements."""
		return sum(self) / len(self)

class BPMCounter:
	"""Give it beats, it'll give you a BPM. And display it too."""

	def __init__(self, filtersize=8):
		self.list = BoundedList(filtersize)
		self.prev = 0

	def beat(self, current=None):
		if current == None:
			current = time.time()

		delta = current - self.prev

		if delta <= 0.01: # since they're not likely to press more than
		# 100 times a second (6000 bpm), discard super-fast beats
			return

		current_bpm = 60 / delta

		self.prev = current
		self.list.push(current_bpm)
		self.bpm = self.list.average() 

	def show(self):
		sys.stdout.write('\tBPM: %d                           \r' % self.bpm)
		sys.stdout.flush()

def parse_args():
	parser = argparse.ArgumentParser(description="Press any key to set the" +
		" tempo, and this script will display the approximate tempo of the" +
		" last several presses.\nPress Escape to exit.")

	parser.add_argument("-f", dest="filtersize", required=False, default=8,
		help="Number of previous beats to average for tempo estimate" +
		" (default 8)", type=int)

	return parser.parse_args()

def main():
	args = parse_args()
	print('Press escape to exit.\n')

	bpm_counter = BPMCounter(args.filtersize)

	bpm_counter.beat()
	key = ord(getch())

	while key != 27: # escape
		bpm_counter.beat()
		bpm_counter.show()
		key = ord(getch())

	print('\n')

if __name__ == '__main__':
	main()