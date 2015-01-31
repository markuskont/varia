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


def get_dump_ranges(argv):
	
	for index, value in enumerate(argv):
		if re.match("\+\+\+ Statistics Dump \+\+\+", value):
			print index, value

def traverse_range(start,end,array):

	for i in range(start,end):
		print array[i]

def main():

	args = parse_arguments()
        statistics = openfile(args.stats)

	print statistics[-1]

#	for line in reversed(statistics):
#
#		if re.match("\+\+\+ Statistics Dump \+\+\+", line):
#			break

#	for line in statistics:
#
#		if re.match("\+\+\+ Statistics Dump \+\+\+", line):
#			print statistics.index(line)


if __name__ == "__main__":

        main()
