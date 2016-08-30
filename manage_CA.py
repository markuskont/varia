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
    parser.add_argument('-d', '--datadir', default='/tmp/CA/', help='Absolute path to root directory of generated client keys and certificates')
    parser.add_argument('-o', '--organization', default='Spin TEK AS', help='Certificate organization value')
    parser.add_argument('-m', '--email', default='admin@spin.ee', help='Certificate email')
    parser.add_argument('-ou', '--organizationunit', default='Administration', help='Certificate organization unit value')
    args = parser.parse_args()

    return args

def check_dir(path):

    folder_mask=0700

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
DATADIR = os.path.abspath(ARGS.datadir)
OPENSSL = '/usr/bin/openssl'
KEY_SIZE = 1024
DAYS = 3650
CA_CERT = CADIR + '/' + 'cacert.pem'
CA_KEY = CADIR + '/' + 'cakey.pem'

IP_REGEX = re.compile('(?:\d{1,3}\.){3}\d{1,3}')

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
O                      = %(ORG)s
OU                     = %(ORG_U)s
CN                     = %(FQDN)s
emailAddress           = %(EMAIL)s

[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment

"""

OPENSSL_SAN_TEMPLATE_HEADER= """
subjectAltName = @alt_names

[ alt_names ]
"""

OPENSSL_SAN="""
DNS.%(ID)s = %(SAN)s
"""
OPENSSL_SAN_IP="""
IP.%(ID)s = %(SAN)s
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
        newvalue = DATADIR + '/' + value
        ca_working_folders[key] = newvalue
        check_dir(ca_working_folders[key])

    for node_fqdn, node_alt_name in nodes.iteritems():

        ca_file_paths = {}

        for key, value in ca_working_folders.iteritems():
            ca_file_paths[key] = value + '/' + node_fqdn + '.' + key

        #hostname = pattern_hostname_from_fqdn.match(node_fqdn).group(1)

        with open (ca_file_paths.get('conf'), 'w') as config:
            config.write(OPENSSL_CONFIG_TEMPLATE % {'FQDN': node_fqdn, 'ORG': ARGS.organization, 'ORG_U': ARGS.organizationunit, 'EMAIL': ARGS.email})
            if node_alt_name:
                config.write(OPENSSL_SAN_TEMPLATE_HEADER)
                if type(node_alt_name) is list:
                    dns_index=1
                    ip_index=1
                    for name in node_alt_name:
                        if IP_REGEX.match(name):
                            config.write(OPENSSL_SAN_IP % {'ID': str(ip_index), 'SAN': name})
                            ip_index = ip_index + 1
                        else:
                            config.write(OPENSSL_SAN % {'ID': str(dns_index), 'SAN': name})
                            dns_index = dns_index + 1
                elif type(node_alt_name) is str:
                    if IP_REGEX.match(name):
                        ip_index=1
                        config.write(OPENSSL_SAN_IP % {'ID': str(dns_index), 'SAN': node_alt_name})
                    else:
                        dns_index=1
                        config.write(OPENSSL_SAN_DNS % {'ID': str(dns_index), 'SAN': node_alt_name})



        if not os.path.isfile(ca_file_paths.get('key')):

            openssl_keygen_arguments = [
                'genrsa',
                '-out',
                ca_file_paths.get('key'),
                str(KEY_SIZE)
            ]

            openssl(openssl_keygen_arguments)
            os.chmod(ca_file_paths.get('key'), 0600)

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

    if not os.path.exists(CADIR):
        print "CA filesystem root directory does not exist!"
        print "Please consider creating with the following command:"
        print "mkdir %s && chmod 700 %s" %(CADIR, CADIR)
        sys.exit(1)
    if not os.path.exists(DATADIR):
        print "Data filesystem root directory does not exist!"
        print "Please consider creating with the following command:"
        print "mkdir %s && chmod 700 %s" %(DATADIR, DATADIR)
        sys.exit(1)
    if not os.path.isfile(CA_KEY):
        print "CA Key file does not exist!"
        print "Please consider creating with the following command:"
        print "openssl genrsa -out %s/cakey.pem 4096 && chmod 0600 %s/cakey.pem" %(CADIR,CADIR)
        sys.exit(1)
    if not os.path.isfile(CA_CERT):
        print "CA Certificate file does not exist!"
        print "Please consider creating with the following command:"
        print "openssl req -new -x509 -days 3650 -key %s/cakey.pem -out %s/cacert.pem" % (CADIR,CADIR)
        sys.exit(1)
    if not os.path.isfile(ALT_NAME_MAP_SOURCE):
        print "No configuration file with node definitions and subject alternative name mappings!"
        #print "Creating %s" % (ALT_NAME_MAP_SOURCE)
        #data = extract_nodes_from_puppet_env()
        #with open(ALT_NAME_MAP_SOURCE, 'w') as outfile:
        #    outfile.write ( yaml.dump(data, default_flow_style=False))
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
