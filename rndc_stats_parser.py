#!/usr/bin/env python

import sys, os, argparse, re, json
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
	def __init__(self):
		self.counters = {}
		
	def __str__(self):
		return "View %s" % str(self.counters)
	

def main():

	args = parse_arguments()
        statistics = openfile(args.stats)

	stats = Statistics()
	counters = {}

	for line in reversed(statistics):

		if re.match("^\s+(\d+) (CNAME)", line):
			m = re.match("^\s+(\d+) (CNAME)", line)
			counters[m.group(2)] = m.group(1)

		if re.match("\[View: .+\]", line):

			views = View()
			#views.counters[line] = line
			views.counters = counters

			stats.sections.append(views)

			#reset temp counters
			counters = {}

			print line

		if re.match("\+\+ .+ \+\+", line):
			print line
		if re.match("\+\+\+ Statistics Dump \+\+\+", line):
			print line
			break

	print(views)
	print(stats)

if __name__ == "__main__":

        main()
