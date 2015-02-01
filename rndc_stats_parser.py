#!/usr/bin/env python

import sys, os, argparse, re, json, copy
from pprint import pprint

def parse_arguments():

        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--stats', help='Text file that contains RNDC statistics output.')
        args = parser.parse_args()

        return args

def openfile(argv):

        with open(argv, 'r') as file:
                lines = [line.rstrip('\n') for line in file]

        return lines

class Statistics():

	def __init__(self):
		self.sections = []
		
	def __str__(self):
		return "Statistics %s" % map(str, self.sections)

class View():
	def __init__(self, init_counters):
		self.counters = {}
		if init_counters:
			self.counters = init_counters
		
	def __str__(self):
		return "View %s" % str(self.counters)
	

def main():

	args = parse_arguments()
        statistics = openfile(args.stats)

	stats = Statistics()
	counters = {}
	sections = {}

	# Hetkel kalane loogika
	# Nii peaks olema
	# view -> section -> statistics

	for line in reversed(statistics):

		if re.match("^\s+(\d+) (.+)", line):
			m = re.match("^\s+(\d+) (.+)", line)
			counters[m.group(2)] = m.group(1)

		if re.match("\[View: (.+)\]", line):

			stats.sections.append(View(counters))

		if re.match("\+\+ .+ \+\+", line):

		if re.match("\+\+\+ Statistics Dump \+\+\+", line):
			break

#	print(views)
	print(stats)

if __name__ == "__main__":

        main()
