#!/usr/bin/env python

import sys, os, argparse, re, json, copy, shelve
from pprint import pprint

def rndc_rtt():

	data = { 
	# resolver stats
	'queries with RTT < 10ms' : 'rtt__10',
	'queries with RTT 10-100ms' : 'rtt_10_100',
	'queries with RTT 100-500ms' : 'rtt_100_500',
	'queries with RTT 500-800ms' : 'rtt_500_800',
	'queries with RTT 800-1600ms' : 'rtt_800_1600',
	'queries with RTT > 1600ms' : 'rtt_1600_'
	 }

	return data

def invoke_rndc_stats(stats_file_path, remfile):

	cmd='rndc stats'

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

def rndc_parser(raw_data):

	stats = {}

	culm_rtt10 = 0
	key_rtt10 = ""
	rtt10 = re.compile('^\s*(\d+) (queries with RTT < 10ms)')
	culm_rtt10100 = 0
	key_rtt10100 = ""
	rtt10100 = re.compile('^\s*(\d+) (queries with RTT 10-100ms)')
	culm_rtt100500 = 0
	key_rtt100500 = ""
	rtt100500 = re.compile('^\s*(\d+) (queries with RTT 100-500ms)')
	culm_rtt500800 = 0
	key_rtt500800 = ""
	rtt500800 = re.compile('^\s*(\d+) (queries with RTT 500-800ms)')
	culm_rtt8001600 = 0
	key_rtt8001600 = ""
	rtt8001600 = re.compile('^\s*(\d+) (queries with RTT 800-1600ms)')
	culm_rtt1600 = 0
	key_rtt1600 = ""
	rtt1600 = re.compile('^\s*(\d+) (queries with RTT > 1600ms)')

	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+ \((\d+)\)")

	for line in reversed(raw_data):
		if dump_regex.match(line):
			break
		elif rtt10.match(line):
			value = int(rtt10.match(line).group(1))
			key_rtt10 = "rtt__10"
			culm_rtt10 = culm_rtt10 + value
		elif rtt10100.match(line):
			value = int(rtt10100.match(line).group(1))
			key_rtt10100 = "rtt_10_100"
			culm_rtt10100 = culm_rtt10100 + value
		elif rtt100500.match(line):
			value = int(rtt100500.match(line).group(1))
			key_rtt100500 = "rtt_100_500"
			culm_rtt100500 = culm_rtt100500 + value
		elif rtt500800.match(line):
			value = int(rtt500800.match(line).group(1))
			key_rtt500800 = "rtt_500_800"
			culm_rtt500800 = culm_rtt500800 + value
		elif rtt8001600.match(line):
			value = int(rtt8001600.match(line).group(1))
			key_rtt8001600 = "rtt_800_1600"
			culm_rtt8001600 = culm_rtt8001600 + value
		elif rtt1600.match(line):
			value = int(rtt1600.match(line).group(1))
			key_rtt1600 = "rtt_1600_"
			culm_rtt1600 = culm_rtt1600 + value

	if key_rtt10:
		stats[key_rtt10] = culm_rtt10
	if key_rtt10100:
		stats[key_rtt10100] = culm_rtt10100
	if key_rtt100500:
		stats[key_rtt100500] = culm_rtt100500
	if key_rtt500800:
		stats[key_rtt500800] = culm_rtt500800
	if key_rtt8001600:
		stats[key_rtt8001600] = culm_rtt8001600
	if key_rtt1600:
		stats[key_rtt1600] = culm_rtt1600

	return stats

def main():

	stats_file_path = '/var/cache/bind/named.stats'
	persist_database_path = '/tmp/rndc_stats.db'

	remove_stats_file_after_invoke = True

        raw_data = invoke_rndc_stats(stats_file_path, remove_stats_file_after_invoke)

	stats = rndc_parser(raw_data)

	for k, v in stats.items():
		#print "%s:%s" % (k,v)
		line = k + ":" + str(v)
		print line,	

if __name__ == "__main__":

        main()
