#!/usr/bin/env python

import sys, os, argparse, re, json, copy, shelve
from pprint import pprint

# Not used ATM
def parse_arguments():

        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--stats', help='Text file that contains RNDC statistics output.')
        args = parser.parse_args()

        return args

def invoke_rndc_stats(stats_file_path, remfile):

	cmd='sudo rndc stats'

	try:
		os.popen(cmd)

	except OSError as e:
		error_message = "%s execution failed" % cmd
		print >>sys.stderr, error_message, e

	if os.path.isfile(stats_file_path):
		try:
			raw_data = openfile(stats_file_path)
		except OSError as e:
			error_message = "%s file open failed" % stats_file_path
			print >>sys.stderr, error_message, e
	else:
		error_message = "%s does not exist in system, or insufficient permissions" % stats_file_path
		print >>sys.stderr, error_message, e

	# let file remove be optional
	if remfile == True:
		try:
			os.remove(stats_file_path)
		except OSError as e:
                        error_message = "%s file remove failed, or insufficient permissions" % stats_file_path
                        print >>sys.stderr, error_message, e

	return raw_data


def openfile(argv):

        with open(argv, 'r') as file:
                lines = [line.rstrip('\n') for line in file]

        return lines

def parse_stats(raw, record_regex, view_regex, subsection_regex, dump_regex):

	counters = {}
	subsections = {}
	views = {}
	dump_mapped = {}

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
			unix_epoch = dump_regex.match(line).group(1)
			dump_mapped[unix_epoch] = subsections
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

	for k, v_new in dict_new.items():
		if isinstance(v_new, dict):
			print "{0}".format(k)
			dictionary_diff(v_new, dict_old.get(k, 0))
		else:
			v_new = int(v_new)
			v_old = int(dict_old.get(k, 0))
			dict_diff = v_new - v_old

			# if counters have reset since last poll, it is safe to use last data
			if dict_diff < 0:
				dict_diff = v_new

			print "{0} : {1}".format(k, str(dict_diff))

def calculate_queries_per_second(new_value,old_value,period):
	pass

def myprint(d):
	for k, v in d.iteritems():
		if isinstance(v, dict):
			print "{0}".format(k)
			myprint(v)
		else:
			print "{0} : {1}".format(k, v)

def main():

	# I will semi-hardcode my paths, because code is going to remove them
	# I do not want to rm arbitrary file, because I messed up an argument
	#args = parse_arguments()
	stats_file_path = '/var/cache/bind/named.stats'
	persist_database_path = '/tmp/test.db'

	# Works, but off for debugging
	# Enable in prod
	remove_stats_file_after_invoke = False
	
        raw_data = invoke_rndc_stats(stats_file_path, remove_stats_file_after_invoke)

	record_regex=re.compile("^\s+(\d+) (.+)")
	subsection_regex=re.compile("\+\+ (.+) \+\+")
	view_regex=re.compile("(?:\[View: (.+)\])")
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+ \((\d+)\)")

	parsed_stats_new = parse_stats(raw_data, record_regex, view_regex, subsection_regex, dump_regex)

	# If database file is present in system
	# Load old database and diff old and new
	if os.path.isfile(persist_database_path):
		parsed_stats_old = load_persistent_dictionary(persist_database_path)
	else:
		parsed_stats_old = parsed_stats_new

	dictionary_diff(parsed_stats_new, parsed_stats_old)

	# Store new data in dict
	store_persistent_dictionary(persist_database_path,parsed_stats_new)

	
	#######################################################
	# Debug section
	# store_persistent_dictionary('/tmp/diff.db', diff)

	# myprint(parsed_stats_new)

if __name__ == "__main__":

        main()
