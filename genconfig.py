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

def main():

	args = parse_arguments()
	listfile = args.list
	templatefile = args.template

	if not listfile: 
		sys.exit('List file not provided')
	elif not templatefile:
		sys.exit('Temlate file not provided')
	else:
		print args

	check_file(listfile, templatefile)

if __name__ == "__main__":

	main()
