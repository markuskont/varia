#!/usr/bin/env python

import sys, os, argparse, re, json, copy

######################################
# CODE EXAMPLES AND DEBUG STUFF
# NOT TO BE USED IN CORE FUNCTIONALITY
######################################

mapping = {
'2001:470:e5bf:dead:4957:2174:e82c:4887':'10.21.74.87',
}

############################
# START NODE EXTRACTION PART
############################

def parse_arguments(environments):

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--environment', choices=environments, default='production', help='Puppet environment')
	args = parser.parse_args()

	return args

def recursive_file_gen(rootdir, pattern):
	for root, dirs, filenames in os.walk(rootdir):
		for filename in filenames:
			if pattern.match(filename):
				yield os.path.join(root, filename)

def extract_data_from_file(files, pattern):

	results = []
	
	for filename in files:
		fd = open(filename)

		
		for line in fd:
			if pattern.match(line):
				results.append(pattern.match(line).group(1))
		fd.close()

	return results

def extract_nodes_from_puppet_env():
	
	rootdir="/etc/puppet/environments/"
	puppet_env_dirs = os.listdir(rootdir)

	args = parse_arguments(puppet_env_dirs)
	selected_env = args.environment

	pattern_puppet_site_manifest = re.compile('site\S+\.pp')
	pattern_puppet_node_definition = re.compile("^node\s+'(\S+)'\s*\{")

	rootdir=rootdir + selected_env + '/'

	print "Environment: " + rootdir

	files = list(recursive_file_gen(rootdir, pattern_puppet_site_manifest))

	nodes = extract_data_from_file(files, pattern_puppet_node_definition)

	for node in nodes:
		print node

##########################################
# END NODE EXTRACTION PART
# START OPENSSL PART
# CREDIT GOES WHERE CREDIT IS DUE:
# https://gist.github.com/toolness/3073310
##########################################

MYDIR = os.path.abspath(os.path.dirname(__file__))
OPENSSL = '/usr/bin/openssl'
KEY_SIZE = 1024
DAYS = 3650
CA_CERT = 'ca.cert'
CA_KEY = 'ca.key'

OPENSSL_CONFIG_TEMPLATE = """
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[ req_distinguished_name ]
C                      = EE
ST                     = Harjumaa
L                      = Tallinn
O                      = Spin TEK AS
OU                     = Administration
CN                     = %(domain)s
emailAddress           = admin@spin.ee

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = %(domain)s
DNS.2 = *.%(domain)s
"""

def openssl(*args):
	cmdline = [OPENSSL] + list(args)
	subprocess.check_call(cmdline)

##################
# END OPENSSL PART
##################

def main():

	extract_nodes_from_puppet_env()

if __name__ == "__main__":

        main()
