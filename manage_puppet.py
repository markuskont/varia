#!/usr/bin/env python

import sys, os, argparse, re, json, copy

mapping = {
'2001:470:e5bf:dead:4957:2174:e82c:4887':'10.21.74.87',
}

def parse_arguments(environments):

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--environment', choices=environments, default='production', help='Puppet environment')
	args = parser.parse_args()

#	if len(sys.argv) < 2:
#		parser.print_help()
#		sys.exit(3)
#
	return args

def recursive_file_gen(rootdir, pattern):
	for root, dirs, filenames in os.walk(rootdir):
		for filename in filenames:
			if pattern.match(filename):
				yield os.path.join(root, filename)

def extract_data_from_file(files, pattern):
	
	for filename in files:
		print filename

def main():

	rootdir="/etc/puppet/environments/"
	puppet_env_dirs = os.listdir(rootdir)

	args = parse_arguments(puppet_env_dirs)
	selected_env = args.environment

	pattern_puppet_site_manifest = re.compile('site\S+\.pp')
	pattern_puppet_node_definition = re.compile("^node\s+'(\S+)'\s*\{")
#	node '1204-test.spin.sise' {
#	pattern_puppet_environment_folder = re.compile('^\S+environments/(\S+)/\S+$')

	rootdir=rootdir + selected_env + '/'

	print "You have selected: " + rootdir

	files = list(recursive_file_gen(rootdir, pattern_puppet_site_manifest))

	extract_data_from_file(files)

if __name__ == "__main__":

        main()
