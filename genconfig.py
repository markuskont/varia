#!/usr/bin/env python

import sys, os, argparse

def parse_arguments():

	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--list', help='Text file that contains a list of data separated by newline.')
	parser.add_argument('-t', '--template', help='Configuration file template.')
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

def print_config(vhosts, template_lines):

	for vhost in vhosts:
		for line in template_lines:
			print line

def main():

	args = parse_arguments()
	listfile = args.list
	templatefile = args.template

	if not listfile: 
		sys.exit('List file not provided')
	elif not templatefile:
		sys.exit('Temlate file not provided')
	elif os.path.isfile(listfile) and os.path.isfile(templatefile):
		vhosts = openfile(listfile)
		template_lines = openfile(templatefile)
		print_config(vhosts, template_lines)
	else:
		sys.exit('Unhandled problem')
		
if __name__ == "__main__":

	main()
