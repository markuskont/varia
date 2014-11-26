#!/usr/bin/env python

import sys, os, argparse

def parse_arguments():

	parser = argparse.ArgumentParser()
	parser.add_argument('-l', '--list', help='Text file that contains a list of data separated by newline.')
	args = parser.parse_args()

	return args
	

def openfile(argv):

	with open(argv, 'r') as file:
		lines = [line.rstrip('\n') for line in file]

	return lines 

def genconfig(argv):
	print argv

def do_stuff():

	if sys.argv[1:]:

		filename = sys.argv[1]

		if os.path.isfile(filename):
			lines = openfile(filename)
			print lines
		else:
			print("%s does not exist or is not a file" % filename)

	else:
		print "Usage: genconfig.py <filename>"

def main():

	args = parse_arguments()

	print args.list


if __name__ == "__main__":

	main()
