#!/usr/bin/env python

import sys, os, argparse, re, json, copy, subprocess, hashlib, datetime
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
	parser.add_argument('-d', '--cadir', default='/tmp/CA/', help='Absolute path to CA root directory')
	args = parser.parse_args()

	return args

def check_dir_list(args_list):

	folder_mask=0700

	for path in args_list:
		if not os.path.exists(path):
			os.mkdir(path)
		if str(oct(os.stat(path)[ST_MODE])[-4:]) != str(folder_mask):
			os.chmod(path, folder_mask)

def validate_CA_files():

	if not os.path.exists(CADIR):
		print "CA filesystem root does not exist!"
		print "Please consider creating with the following command:"
		print "mkdir %s && chmod 700 %s" %(CADIR, CADIR)
		sys.exit(2)
	if not os.path.isfile(CA_KEY):
		print "CA Key file does not exist!"
		print "Please consider creating with the following command:"
		print "openssl genrsa -out %s/cakey.pem 4096 && chmod 0600 %s/cakey.pem" %(CADIR,CADIR)
		sys.exit(2)
	if not os.path.isfile(CA_CERT):
		print "CA Certificate file does not exist!"
		print "Please consider creating with the following command:"
		print "openssl req -new -x509 -days 3650 -key %s/cakey.pem -out %s/cacert.pem" % (CADIR,CADIR)
		sys.exit(2)
			
		
# GLOBAL VARIABLES
PUPPET_ROOT_DIR="/etc/puppet/environments/"
PUPPET_ENV_DIRS = os.listdir(PUPPET_ROOT_DIR)
ARGS = parse_arguments(PUPPET_ENV_DIRS)
SELECTED_ENV = ARGS.environment
CADIR = os.path.abspath(ARGS.cadir)
OPENSSL = '/usr/bin/openssl'
KEY_SIZE = 1024
DAYS = 3650
CA_CERT = CADIR + '/' + 'cacert.pem'
CA_KEY = CADIR + '/' + 'cakey.pem'

X509_EXTRA_ARGS = ()

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

def extract_nodes_from_puppet_env():
	
	puppet_rootdir=PUPPET_ROOT_DIR + SELECTED_ENV + '/'
	

	pattern_puppet_site_manifest = re.compile('site\S+\.pp')
	pattern_puppet_node_definition = re.compile("^node\s+'(\S+)'\s*\{")

	files = list(recursive_file_gen(puppet_rootdir, pattern_puppet_site_manifest))

	nodes = extract_data_from_file(files, pattern_puppet_node_definition)

	# DEBUG OUTPUT
	print "Environment: " + puppet_rootdir
	print "CA root dir: " + CADIR
	print "CA key file: " + CA_KEY
	print "CA certificate file: " + CA_CERT
	# END DEBUG OUTPUT

	return nodes

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
CN                     = %(fqdn)s.spin.ee
emailAddress           = admin@spin.ee

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

subjectAltName = @alt_names

[ alt_names ]
DNS.1 = %(fqdn)s
DNS.2 = %(fqdn)s
"""

def openssl(*args):
	cmdline = [OPENSSL] + list(args)
	subprocess.check_call(cmdline)

def gencert(nodes, rootdir=CADIR, keysize=KEY_SIZE, days=DAYS, ca_cert=CA_CERT, ca_key=CA_KEY):

	pattern_hostname_from_fqdn = re.compile("(\S+)\.\S+\.\S+$")

	ca_working_folders = [ 'config.d', 'requests', 'private', 'certificates']
	ca_working_folders = [ CADIR + '/' + folder for folder in ca_working_folders]

#	ca_config_rootdir=ca_working_folders[0]
#	ca_req_rootdir=ca_working_folders[1]
#	ca_key_rootdir=ca_working_folders[2]
#	ca_cert_rootdir=ca_working_folders[3]

	check_dir_list(ca_working_folders)

	for node_fqdn in nodes:

		hostname = pattern_hostname_from_fqdn.match(node_fqdn).group(1)

		conf_file_abs_path = ca_working_folders[0] + '/' + node_fqdn + '.conf'
		req_file_abs_path = ca_working_folders[1] + '/' + node_fqdn + '.csr'
		key_file_abs_path = ca_working_folders[2] + '/' + node_fqdn + '.key'
		cert_file_abs_path = ca_working_folders[3] + '/' + node_fqdn + '.cert'

		config = open(conf_file_abs_path, 'w')
		config.write(OPENSSL_CONFIG_TEMPLATE % {'fqdn': hostname})
		config.close()

		if not os.path.isfile(key_file_abs_path):
			openssl('genrsa', '-out', key_file_abs_path, str(keysize))

		if not os.path.isfile(cert_file_abs_path):
			openssl('req', '-new', '-key', key_file_abs_path, '-out', req_file_abs_path, '-config', conf_file_abs_path)
			openssl('x509', '-req', '-days', str(days), '-in', req_file_abs_path, '-CA', ca_cert, '-CAkey', ca_key, '-set_serial', '0x%s' % hashlib.md5(node_fqdn + str(datetime.datetime.now())).hexdigest(), '-out', cert_file_abs_path, '-extensions', 'v3_req', '-extfile', conf_file_abs_path, *X509_EXTRA_ARGS)

##################
# END OPENSSL PART
##################

def main():

	validate_CA_files()
	nodes = extract_nodes_from_puppet_env()
	gencert(nodes)

if __name__ == "__main__":

        main()
