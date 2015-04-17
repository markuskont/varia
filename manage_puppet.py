#!/usr/bin/env python

import sys, os, argparse, re, json, copy, subprocess
from stat import *

######################################
# CODE EXAMPLES AND DEBUG STUFF
# NOT TO BE USED IN CORE FUNCTIONALITY
######################################

mapping = {
'2001:470:e5bf:dead:4957:2174:e82c:4887':'10.21.74.87',
}

####################
# START SHARED LOGIC
####################

def parse_arguments(environments):

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--environment', choices=environments, default='production', help='Puppet environment')
	parser.add_argument('-d', '--cadir', default='/tmp/', help='Absolute path to CA root directory')
	args = parser.parse_args()

	return args

# For intents and purposes, this is functionally main();
# At least for now
def extract_nodes_from_puppet_env():
	
	puppet_rootdir=PUPPET_ROOT_DIR + SELECTED_ENV + '/'
	

	pattern_puppet_site_manifest = re.compile('site\S+\.pp')
	pattern_puppet_node_definition = re.compile("^node\s+'(\S+)'\s*\{")
	pattern_hostname_from_fqdn = re.compile("(\S+)\.\S+\.\S+$")

	files = list(recursive_file_gen(puppet_rootdir, pattern_puppet_site_manifest))

	nodes = extract_data_from_file(files, pattern_puppet_node_definition)

	ca_working_folders = [ 'config.d', 'requests', 'private', 'certificates']
	ca_working_folders = [ CADIR + '/' + folder for folder in ca_working_folders]

	# replace this part
#	ca_config_rootdir=CADIR + '/' + 'config.d' 
#	ca_req_rootdir=CADIR + '/' + 'requests' 
#	ca_key_rootdir=CADIR + '/' + 'keys' 
#	ca_cert_rootdir=CADIR + '/' + 'certificates' 
	ca_config_rootdir=ca_working_folders[0]
	ca_req_rootdir=ca_working_folders[1]
	ca_key_rootdir=ca_working_folders[2]
	ca_cert_rootdir=ca_working_folders[3]

	check_dir_list(ca_working_folders)

	for node_fqdn in nodes:

		hostname = pattern_hostname_from_fqdn.match(node_fqdn).group(1)

		config_file_abs_path = ca_config_rootdir + '/' + node_fqdn + '.conf'
		#key_file_abs_path = CADIR + '/'
		#req_file_abs_path = ca_config_rootdir + '/' + node_fqdn + '.conf'

		config = open(config_file_abs_path, 'w')
		config.write(OPENSSL_CONFIG_TEMPLATE % {'hostname': hostname})
		config.close()

		#openssl('req', '-new', '-key', dfile('key'), '-out', dfile('request'), '-config', config_file_abs_path)

	# DEBUG OUTPUT
	print "Environment: " + puppet_rootdir
	print "CA root dir: " + CADIR
	print "CA key file: " + CA_KEY
	print "CA certificate file: " + CA_CERT
	# END DEBUG OUTPUT

def check_dir_list(args_list):

	folder_mask=0700

	for path in args_list:
		if not os.path.exists(path):
			os.mkdir(path)
		if str(oct(os.stat(path)[ST_MODE])[-4:]) != str(folder_mask):
			os.chmod(path, folder_mask)
			
		
# GLOBAL VARIABLES
PUPPET_ROOT_DIR="/etc/puppet/environments/"
PUPPET_ENV_DIRS = os.listdir(PUPPET_ROOT_DIR)
ARGS = parse_arguments(PUPPET_ENV_DIRS)
SELECTED_ENV = ARGS.environment
CADIR = os.path.abspath(ARGS.cadir)
OPENSSL = '/usr/bin/openssl'
KEY_SIZE = 1024
DAYS = 3650
# TODO: Validate presence of files!
CA_CERT = CADIR + '/' + 'cacert.pem'
CA_KEY = CADIR + '/' + 'cakey.pem'

############################
# END SHARED LOGIC
# START NODE EXTRACTION PART
############################

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

##########################################
# END NODE EXTRACTION PART
# START OPENSSL PART
# CREDIT GOES WHERE CREDIT IS DUE:
# https://gist.github.com/toolness/3073310
##########################################


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
CN                     = %(hostname)s.spin.ee
emailAddress           = admin@spin.ee

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = %(hostname)s.spin.sise
DNS.2 = %(hostname)s.keskus.sise
"""

def openssl(*args):
	cmdline = [OPENSSL] + list(args)
	subprocess.check_call(cmdline)

def gencert(fqdn, rootdir=CADIR, keysize=KEY_SIZE, days=DAYS, ca_cert=CA_CERT, ca_key=CA_KEY):
	pass
	

##################
# END OPENSSL PART
##################

def main():

	extract_nodes_from_puppet_env()

if __name__ == "__main__":

        main()
