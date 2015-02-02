#!/usr/bin/env python

import sys, os, argparse, re, json, copy, shelve
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

def parse_stats(raw, record_regex, view_regex, subsection_regex, dump_regex):

	counters = {}
	subsections = {}
	views = {}

	# Hetkel kalane loogika
	# Nii peaks olema
	# view -> section -> statistics

	for line in reversed(raw):

		if record_regex.match(line):
			m = record_regex.match(line)
			counters[m.group(2)] = m.group(1)

		elif view_regex.match(line):
			if counters:
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

	return subsections


def store_persistent_dictionary(path,d):

	s = shelve.open(path)
	try:
		s['key1'] = d
	finally:
		s.close()

def load_persistent_dictionary(path):

	s = shelve.open(path)
	try:
		existing = s['key1']
	finally:
		s.close()
		return existing

def dictionary_diff(dict_new,dict_old):

	dict_diff = {}

	for k, v_new in dict_new.items():
		if isinstance(v_new, dict):
			dict_diff = dictionary_diff(v_new, dict_old.get(k, 0))
		else:
			v_new = int(v_new)
			v_old = int(dict_old.get(k, 0))
			dict_diff[k] = v_new - v_old
			return dict_diff

	return dict_diff

def myprint(d):
	for k, v in d.iteritems():
		if isinstance(v, dict):
			print "{0}".format(k)
			myprint(v)
		else:
			print "{0} : {1}".format(k, v)

def main():

	args = parse_arguments()
        raw_data = openfile(args.stats)

	record_regex=re.compile("^\s+(\d+) (.+)")
	subsection_regex=re.compile("\+\+ (.+) \+\+")
	view_regex=re.compile("(?:\[View: (.+)\])")
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+")

	persist_database_path = '/tmp/test.db'

	parsed_stats_old = load_persistent_dictionary(persist_database_path)
	parsed_stats_new = parse_stats(raw_data, record_regex, view_regex, subsection_regex, dump_regex)

	store_persistent_dictionary(persist_database_path,parsed_stats_new)

	diff = dictionary_diff(parsed_stats_new, parsed_stats_old)

	myprint(parsed_stats_new)

	#myprint(parsed_stats_new)

if __name__ == "__main__":

        main()
