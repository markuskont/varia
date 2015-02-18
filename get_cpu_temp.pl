#!/usr/bin/env perl
use strict;
use warnings;

my $cmd = "sensors";    
my @output = `$cmd`;    
chomp @output;

foreach my $line (@output)
{
	if($line =~ m/^(Core) (\d):\s+[+-]?(\d+)\.\d+\s*C/){

		print "$1:".$3;

	}

}
