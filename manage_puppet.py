#!/usr/bin/env python

import sys, os, argparse, re, json, copy, subprocess, hashlib, datetime, yaml
from stat import *

####################
# START SHARED LOGIC
####################

def parse_arguments(environments):

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--environment', choices=environments, default='production', help='Puppet environment')
	parser.add_argument('-c', '--cadir', default='/tmp/CA/', help='Absolute path to CA root directory')
	#parser.add_argument('-d', '--datadir', default='/tmp/CA/', help='Absolute path to CA root directory')
	#parser.add_argument('-m', '--mapfile', default='/tmp/CA/alt_name_map.yaml', help='Config file, which contains node definitions.')
	args = parser.parse_args()

	return args

def check_dir(path):

	folder_mask=0700

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

ALT_NAME_MAP_SOURCE = CADIR + '/' + 'node_map.yaml'

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

	results = {}
	
	for filename in files:
		fd = open(filename)

		for line in fd:
			if pattern.match(line):
				results[pattern.match(line).group(1)] = ''
		fd.close()

	return results

def extract_nodes_from_puppet_env():
	
	puppet_rootdir=PUPPET_ROOT_DIR + SELECTED_ENV + '/'
	

	pattern_puppet_site_manifest = re.compile('site\S+\.pp')
	pattern_puppet_node_definition = re.compile("^node\s+'(\S+)'\s*\{")

	files = list(recursive_file_gen(puppet_rootdir, pattern_puppet_site_manifest))

	return extract_data_from_file(files, pattern_puppet_node_definition)

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
CN                     = %(FQDN)s
emailAddress           = admin@spin.ee

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

"""

OPENSSL_SAN_TEMPLATE= """
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = %(SAN)s
"""


def openssl(argument_list):
	cmdline = [OPENSSL] + argument_list
	subprocess.check_call(cmdline)

def gencert(nodes):

	pattern_hostname_from_fqdn = re.compile("(\S+)\.\S+\.\S+$")

	ca_working_folders =	{	
					'conf':'config.d', 
					'csr':'requests', 
					'key':'private',
					'cert':'certificates',
				}

	for key, value in ca_working_folders.iteritems():
		newvalue = CADIR + '/' + value
		ca_working_folders[key] = newvalue
		check_dir(ca_working_folders[key])

	for node_fqdn, node_alt_name in nodes.iteritems():

		ca_file_paths = {}
		
		for key, value in ca_working_folders.iteritems():
			ca_file_paths[key] = value + '/' + node_fqdn + '.' + key

		#hostname = pattern_hostname_from_fqdn.match(node_fqdn).group(1)

		with open (ca_file_paths.get('conf'), 'w') as config:
			config.write(OPENSSL_CONFIG_TEMPLATE % {'FQDN': node_fqdn})
			if node_alt_name:
				config.write(OPENSSL_SAN_TEMPLATE % {'SAN': node_alt_name})



		if not os.path.isfile(ca_file_paths.get('key')):

			openssl_keygen_arguments = [
				'genrsa',
				'-out',
				ca_file_paths.get('key'),
				str(KEY_SIZE)
			]

			openssl(openssl_keygen_arguments)

		if not os.path.isfile(ca_file_paths.get('cert')):

			openssl_csr_arguments = [
				'req',
				'-new',
				'-key',
				ca_file_paths.get('key'),
				'-out',
				ca_file_paths.get('csr'),
				'-config',
				ca_file_paths.get('conf'),
			]

			openssl_signature_arguments = [
				'x509',
				'-req',
				'-days',
				str(DAYS),
				'-in',
				ca_file_paths.get('csr'),
				'-CA',
				CA_CERT,
				'-CAkey',
				CA_KEY,
				'-set_serial',
				'0x%s' % hashlib.md5(node_fqdn + str(datetime.datetime.now())).hexdigest(),
				'-out',
				ca_file_paths.get('cert'),
				'-extensions',
				'v3_req',
				'-extfile',
				ca_file_paths.get('conf'),
			]

			openssl(openssl_csr_arguments)
			openssl(openssl_signature_arguments)

##################
# END OPENSSL PART
##################

def main():

	validate_CA_files()

	if not os.path.isfile(ALT_NAME_MAP_SOURCE):
		print "No configuration file with node definitions and subject alternative name mappings!"
		print "Creating %s" % (ALT_NAME_MAP_SOURCE)
		data = extract_nodes_from_puppet_env()
		with open(ALT_NAME_MAP_SOURCE, 'w') as outfile:
			outfile.write ( yaml.dump(data, default_flow_style=False))
		print "Please verify data in %s and re-execute the script" % (ALT_NAME_MAP_SOURCE)
		sys.exit(1)
	else:
		print "Loading node definitions from %s" % (ALT_NAME_MAP_SOURCE)
		with open (ALT_NAME_MAP_SOURCE, 'r') as infile:
			nodes = yaml.load(infile)

		if type(nodes) is dict:
			print "Generating signed certificates"
			gencert(nodes)
		else:
			print "Data format error"

if __name__ == "__main__":

        main()
