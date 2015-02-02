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

def myprint(d):
	for k, v in d.iteritems():
		if isinstance(v, dict):
			print "{0}".format(k)
			myprint(v)
		else:
			print "{0} : {1}".format(k, v)

def parse_stats(raw, record_regex, view_regex, subsection_regex, dump_regex):

	counters = {}
	subsections = {}
	views = {}

	# Hetkel kalane loogika
	# Nii peaks olema
	# view -> section -> statistics

	for line in reversed(statistics):

		if record_regex.match(line):
			m = record_regex.match(line)
			counters[m.group(2)] = m.group(1)

		elif view_regex.match(line):
			m = view_regex.match(line)
			views[m.group(1)] = counters
			counters = {}

		elif subsection_regex.match(line):
			if not counters and views:
				m = subsection_regex.match(line)
				subsections[m.group(1)] = views
				views = {}
			elif counters and not views:
				m = subsection_regex.match(line)
				subsections[m.group(1)] = counters
				counters = {}

		elif dump_regex.match(line):
			break
		else:
			pass

	myprint(subsections)		

def main():

	args = parse_arguments()
        statistics = openfile(args.stats)

	record_regex=re.compile("^\s+(\d+) (.+)")
	subsection_regex=re.compile("\+\+ (.+) \+\+")
	view_regex=re.compile("(?:\[View: (.+)\])")
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+")

	parse_stats(statistics, record_regex, view_regex, subsection_regex, dump_regex)

#	print views.items()
#	print subsections.items()

if __name__ == "__main__":

        main()
