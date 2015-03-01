#!/usr/bin/env python

import sys, os, argparse, re, json, copy, shelve
from pprint import pprint


def dictionary_key_substitute():

	substitute = { 
	# resolver stats
	'IPv4 AXFR requested': 'ip4axfrreq',
	'transfer requests failed': 'axfrfail', 
	'IPv4 SOA queries sent' : 'ip4soaq',
	'IPv4 responses received' : 'ip4resp',
	'DNSSEC validation succeeded' : 'dnssecvalsuc',
	'NXDOMAIN received' : 'nxdomain',
	'other errors received' : 'otherr',
	'queries with RTT < 10ms' : 'rtt__10',
	'queries with RTT 10-100ms' : 'rtt_10_100',
	'queries with RTT 100-500ms' : 'rtt_100_500',
	'queries with RTT 500-800ms' : 'rtt_500_800',
	'queries with RTT 800-1600ms' : 'rtt_800_1600',
	'queries with RTT > 1600ms' : 'rtt_1600_',
	'IPv6 queries sent' : 'ip6qsent',
	'IPv4 queries sent' : 'ip4qsent',
	'IPv4 NS address fetches' : 'ip4nsfetch',
	'query retries' : 'qret',
	'query timeouts' : 'qtimeout',
	'IPv4 NS address fetch failed' : 'ip4nsfetchfail',
	'DNSSEC validation attempted' : 'dnssecvalatt',
	'lame delegations received' : 'lamedel',
	'SERVFAIL received' : 'srvfail',
	'DNSSEC NX validation succeeded' : 'dnssecnxvalsuc',
	'IPv6 NS address fetch failed' : 'ip6nsfetchf',
	'truncated responses received' : 'truncresp',
	# Socket I/O
	'UDP/IPv6 sockets closed' : 'u6soccl',
	'TCP/IPv4 connections established' : 't4conest',
	'UDP/IPv6 sockets opened' : 'u6socop',
	'UDP/IPv6 socket connect failures' : 'u6socconf',
	'UDP/IPv4 socket bind failures' : 'u4socbinf',
	'UDP/IPv6 send errors' : 'u6serr',
	'UDP/IPv4 sockets closed' : 'u4sockcl',
	'UDP/IPv4 recv errors' : 'u4rerr',
	'UDP/IPv4 connections established' : 'u4connest',
	'TCP/IPv4 sockets closed' : 't4soccl',
	'TCP/IPv4 socket connect failures' : 't4socconf',
	'TCP/IPv4 sockets opened' : 't4socop',
	'TCP/IPv4 connections accepted' : 't4conacc',
	'UDP/IPv4 sockets opened' : 'u4socop',
	# Name Server Statistics
	'responses with EDNS\(0\) sent' : 'r_edns_s',
	'requests with EDNS\(0\) received' : 'r_edns_r',
	'duplicate queries received' : 'dupqrec',
	'auth queries rejected' : 'authqrej',
	'truncated responses sent' : 'trresps',
	'queries resulted in non authoritative answer' : 'qresnaa',
	'queries resulted in SERVFAIL' : 'qressf',
	'queries resulted in NXDOMAIN' : 'qresnxdom',
	'queries resulted in nxrrset' : 'qresnxrr',
	'responses sent' : 'rests',
	'other query failures' : 'o_qfail',
	'queries resulted in referral answer' : 'qresrefan',
	'recursive queries rejected' : 'recqrej',
	'IPv4 requests received' : 'ip4reqrec',
	'queries resulted in authoritative answer' : 'qresaa',
	'TCP requests received' : 'treqrec',
	'queries resulted in successful answer' : 'qressuca',
	'queries caused recursion' : 'qcaurec'
	 }

	return substitute

# Not used ATM
def parse_arguments():

        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--stats', help='Text file that contains RNDC statistics output.')
        args = parser.parse_args()

        return args

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
			break
		else:
			pass

	return subsections

def get_timestamp(raw, pattern):

	for line in reversed(raw):
		if pattern.match(line):
			
			timestamp = pattern.match(line).group(1)
			break

	return timestamp

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

def dictionary_diff(dict_new,dict_old,timestamp_new,timestamp_old):

	for k, v_new in dict_new.items():
		if isinstance(v_new, dict):
			#print format_key(k),
			dictionary_diff(v_new, dict_old.get(k, 0),timestamp_new,timestamp_old)
		else:
			v_diff = subtract(v_new,dict_old.get(k,0))
			timestamp_diff = subtract(timestamp_new,timestamp_old)

			if v_diff < 0:
				v_diff = v_new

			v_per_second = int(v_diff) #/ float(timestamp_diff)

			print_stats(k,v_per_second)
			#print "{0} : {1}".format(format_key(k), str(v_per_second))

def print_stats(key,value):
	line = format_key(key) + ":" + str(value)
	#print "%s: %s"  % (format_key(key),value)
	print line,

	#print '{0}: "{1}" '.format(format_key(key), str(value))

def format_key(key):


	# Default key names are too long for cacti to handle
	# Create substitutions

	key_string_patterns = dictionary_key_substitute()

	for k, v in key_string_patterns.items():
		if re.match(k, key):
			key = v

	#stripped = re.sub(pattern,'_',key)

	return key

def subtract(new_value,old_value):
	
	diff = int(new_value) - int(old_value)

	return diff

# debug only
def myprint(d):
	for k, v in d.iteritems():
		if isinstance(v, dict):
			print "{0}".format(k)
			myprint(v)
		else:
			print "{0} : {1}".format(k, v)

def main():

	#########################
	# Variables
	#########################
	
	# I will semi-hardcode my paths, because code is going to remove system file
	# I do not want to rm arbitrary file, because I messed up an argument
	#args = parse_arguments()
	stats_file_path = '/var/cache/bind/named.stats'
	persist_database_path = '/tmp/rndc_stats.db'

	# Works, but off for debugging
	# Enable in prod
	remove_stats_file_after_invoke = True

	record_regex=re.compile("^\s+(\d+) (.+)")
	subsection_regex=re.compile("\+\+ (.+) \+\+")
	view_regex=re.compile("(?:\[View: (.+)\])")
	dump_regex=re.compile("\+\+\+ Statistics Dump \+\+\+ \((\d+)\)")

	########################
	# Process data
	########################

        raw_data = invoke_rndc_stats(stats_file_path, remove_stats_file_after_invoke)

	# Currently easier to get separately than attempt to return with parse_stats
	# Timestamp does not play well establised dict structure, and returning multiple distinct values is complicated
	# Refactor later
	timestamp_new = get_timestamp(raw_data, dump_regex)

	parsed_stats_new = parse_stats(raw_data, record_regex, view_regex, subsection_regex, dump_regex)

	# If database file is present in system
	# Load old database
	if os.path.isfile(persist_database_path):
		parsed_stats_old = load_persistent_dictionary(persist_database_path,'statistics')
		timestamp_old = load_persistent_dictionary(persist_database_path, 'timestamp')
	else:
		parsed_stats_old = parsed_stats_new
		timestamp_old = timestamp_new

	# Store new data in dict
	store_persistent_dictionary(persist_database_path,parsed_stats_new,'statistics')
	store_persistent_dictionary(persist_database_path,timestamp_new,'timestamp')

	dictionary_diff(parsed_stats_new, parsed_stats_old, timestamp_new, timestamp_old)


	#######################################################
	# Debug section
	#######################################################

	# store_persistent_dictionary('/tmp/diff.db', diff)
	# print timestamp_new
	# print timestamp_diff
	# myprint(parsed_stats_new)

if __name__ == "__main__":

        main()
