#!/usr/bin/python -u

import sys, os, re

def execute_command():
	cmd='sensors'
    
	return os.popen(cmd).read().split('\n')

def main():
	
	core_temp_regex = re.compile('^(Core \d:)\s+[+-]?(\d+)\.\d+\s*C')

	data_list = execute_command()

	for line in data_list:
		if core_temp_regex.match(line):
			formatted = re.sub('\s','',core_temp_regex.match(line).group(1)) + core_temp_regex.match(line).group(2)
			print formatted,

if __name__ == "__main__":

        main()
