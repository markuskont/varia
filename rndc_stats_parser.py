#!/usr/bin/env python

import sys, os, argparse, re

def parse_arguments():

        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--stats', help='Text file that contains RNDC statistics output.')
        args = parser.parse_args()

        return args

def openfile(argv):

        with open(argv, 'r') as file:
                lines = [line.rstrip('\n') for line in file]

        return lines

class Statistics():

	def __init__(self):
		self.sections = []
		

def main():

	args = parse_arguments()
        statistics = openfile(args.stats)

	for line in reversed(statistics):

		if re.match("\[View: .+\]", line):
			print line
		if re.match("\+\+ .+ \+\+", line):
			print line
		if re.match("\+\+\+ Statistics Dump \+\+\+", line):
			print line
			break


if __name__ == "__main__":

        main()
