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

	record_regex=re.compile("^\s+(\d+) (.+)")
	subsection_regex=re.compile("\+\+ .+ \+\+")
	view_regex=re.compile("\[View: (.+)\]")
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+")

	# Hetkel kalane loogika
	# Nii peaks olema
	# view -> section -> statistics

	for line in reversed(statistics):

		if record_regex.match(line):
			m = record_regex.match(line)
			counters[m.group(2)] = m.group(1)

		elif subsection_regex.match(line):
			pass

		elif view_regex.match(line):
			stats.sections.append(View(counters))

		elif dump_regex.match(line):
			break
		else:
			pass

#	print(views)
	print(stats)

if __name__ == "__main__":

        main()
