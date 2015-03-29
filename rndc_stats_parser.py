#!/usr/bin/env python

import sys, os, argparse, re, json, copy, shelve
from pprint import pprint

def varmap():
	stats = {
	'rtt_10':'^\s*(\d+) queries with RTT < 10ms',
	'rtt10100':'^\s*(\d+) queries with RTT 10-100ms',
	'rtt100500':'^\s*(\d+) queries with RTT 100-500ms',
	'rtt500800':'^\s*(\d+) queries with RTT 500-800ms',
	'rtt8001600':'^\s*(\d+) queries with RTT 800-1600ms',
	'rtt1600':'^\s*(\d+) queries with RTT > 1600ms',
	'u4connest':'^\s*(\d+) UDP/IPv4 connections established',
	'u6connest':'^\s*(\d+) UDP/IPv6 connections established',
	'record_a':'^\s*(\d+) A$',
	'record_aaaa':'^\s*(\d+) AAAA$',
	'record_ns':'^\s*(\d+) NS$',
	'record_cname':'^\s*(\d+) CNAME$',
	'record_mx':'^\s*(\d+) MX$',
	}

	return stats

def store_persistent_dictionary(path,d,key):

        s = shelve.open(path)
        try:
                s[key] = d
        finally:
                s.close()

def load_persistent_dictionary(path,key):

        s = shelve.open(path)
        try:
                existing = s[key]
        finally:
                s.close()
                return existing

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

def subtract(new_value,old_value):

        diff = int(new_value) - int(old_value)

	if diff < 0:
		diff = new_value
	else:
        	diff = diff

        return diff

def parse(raw_data):
	
	stats = varmap()
	#culm = 0
	counter = {}
	break_pattern = ''
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+ \((\d+)\)")

	for line in reversed(raw_data):
		for k, regex in stats.iteritems():

			pattern = re.compile(regex)

			if pattern.match(line):
				if k not in counter:
					counter[k] = 0


				counter[k] = counter[k] + int(pattern.match(line).group(1))

	return counter
	

# This is crap
# Not used
def rndc_parser(raw_data):

	stats = {}

	# Round trip time variables
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

	# Connection variables
	culm_u4connest = 0
	key_u4connest = ""
	u4connest = re.compile('^\s*(\d+) UDP/IPv4 connections established')
	culm_u6connest = 0
	key_u6connest = ""
	u6connest = re.compile('^\s*(\d+) UDP/IPv6 connections established')

	# Record variables
	culm_record_a = 0
	key_record_a = ""
	record_a = re.compile('^\s*(\d+) A$')
	culm_record_aaaa = 0
	key_record_aaaa = ""
	record_aaaa = re.compile('\s*(\d+) AAAA$')
	culm_record_ns = 0
	key_record_ns = ""
	record_ns = re.compile('\s*(\d+) NS$')

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
		elif u4connest.match(line):
			value = int(u4connest.match(line).group(1))
			key_u4connest = "u4connest"
			culm_u4connest = culm_u4connest + value
		elif u6connest.match(line):
			value = int(u6connest.match(line).group(1))
			key_u6connest = "u6connest"
			culm_u6connest = culm_u6connest + value
		elif record_a.match(line):
			value = int(record_a.match(line).group(1))
			key_record_a = "record_a"
			culm_record_a = culm_record_a + value
		elif record_aaaa.match(line):
			value = int(record_aaaa.match(line).group(1))
			key_record_aaaa = "record_aaaa"
			culm_record_aaaa = culm_record_aaaa + value
		elif record_ns.match(line):
			value = int(record_ns.match(line).group(1))
			key_record_ns = "record_ns"
			culm_record_ns = culm_record_ns + value

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
	if key_u4connest:
		stats[key_u4connest] = culm_u4connest
	if key_u6connest:
		stats[key_u6connest] = culm_u6connest
	if key_record_a:
		stats[key_record_a] = culm_record_a
	if key_record_aaaa:
		stats[key_record_aaaa] = culm_record_aaaa
	if key_record_ns:
		stats[key_record_ns] = culm_record_ns

	return stats

def main():

	stats_file_path = '/var/cache/bind/named.stats'
	persist_database_path = '/tmp/rndc_rtt_stats.db'

	remove_stats_file_after_invoke = True

        raw_data = invoke_rndc_stats(stats_file_path, remove_stats_file_after_invoke)

	stats = parse(raw_data)
	stats_diff = {}

	#persistent storage start
	if os.path.isfile(persist_database_path):
                parsed_stats_old = load_persistent_dictionary(persist_database_path,'statistics')
        else:
                parsed_stats_old = stats

	store_persistent_dictionary(persist_database_path,stats,'statistics')

	for k, v in stats.items():
		v_old = parsed_stats_old.get(k, 0)
		stats_diff[k] = subtract(v,v_old)

	for k, v in stats_diff.items():
		#print "%s:%s" % (k,v)
		line = k + ":" + str(v)
		print line,	

if __name__ == "__main__":

        main()
