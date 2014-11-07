#!/usr/bin/perl

sub populateArrayFromFile {

        my ($filename) = @_;

        open FILE, $filename || die "Cannot open file ".$filename." for read";

        @lines=<FILE>;

        close FILE;

        return @lines;

}

foreach my $filename (@ARGV) {

        my @newlines = ();
        my @lines = populateArrayFromFile($filename);
        my $string;
        my $newfilename = $filename . ".new";
        my $backupfile = $filename . ".7112014bak";
        my $logformat;

        rename $filename, $backupfile;

        foreach $line (@lines){

                if($line =~ m/(<\?php.+qV="stop_.+\?>)(.*)/){

                        $string = $2

                } else {

                        $string = $line;

                }

                push(@newlines,$string);

        }

        open(NEWFILE,">$filename") || die "cannot open $filename";

        print NEWFILE @newlines;

        close NEWFILE;

}
