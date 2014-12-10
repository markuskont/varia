#!/usr/bin/env python

import sys, os, argparse, re

def parse_arguments():

	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--list', help='Text file that contains a list of data separated by newline.')
	parser.add_argument('-t', '--template', help='Configuration file template.')
	parser.add_argument('-H', '--hostname', help='Name of nagios HOST value for which the configuration block is generated.')
	args = parser.parse_args()

	return args

def check_file(*args):

	for arg in args:
		if not os.path.isfile(arg):
			sys.exit('Argument not system file.')

def openfile(argv):

	with open(argv, 'r') as file:
		lines = [line.rstrip('\n') for line in file]

	return lines 

def print_config(vhosts, template_lines, nagios_host):

	for vhost in vhosts:
		for line in template_lines:
			line = re.sub("__HOSTNAME__", nagios_host, line) 
			line = re.sub("__VAR1__", vhost, line) 
			print line

def main():

	args = parse_arguments()
	listfile = args.list
	templatefile = args.template
	nagios_host = args.hostname

	if not listfile: 
		sys.exit('List file not provided')
	elif not templatefile:
		sys.exit('Temlate file not provided')
	elif not nagios_host:
		sys.exit('Host name not provided')
	elif os.path.isfile(listfile) and os.path.isfile(templatefile):
		vhosts = openfile(listfile)
		template_lines = openfile(templatefile)
		print_config(vhosts, template_lines, nagios_host)
	else:
		sys.exit('Unhandled problem')
		
if __name__ == "__main__":

	main()
