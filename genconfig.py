#!/usr/bin/env python

import sys, os

def openfile(argv):

	with open(argv) as file:
		lines = [line.rstrip('\n') for line in file]

	return lines 

def genconfig(argv):
	print argv

def main():

	if sys.argv[1:]:

		filename = sys.argv[1]

		if os.path.isfile(filename):
			lines = openfile(filename)
			print lines
		else:
			print("%s does not exist or is not a file" % filename)

	else:
		print "Usage: genconfig.py <filename>"

if __name__ == "__main__":

	main()
