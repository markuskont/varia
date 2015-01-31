#!/usr/bin/env python

import sys, os, argparse, re

def parse_arguments():

        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--stats', help='Text file that contains RNDC statistics output.')
        args = parser.parse_args()

        return args

def main():

	args = parse_arguments()
        statsfile = args.stats


if __name__ == "__main__":

        main()
