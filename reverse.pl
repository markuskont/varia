#!/usr/bin/env perl


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

        foreach $line (@lines) {

                if ($line =~ m/\d{1,3}\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\S*\s+(\S+)/) {
                        print "$3.$2.$1         IN    PTR    $4.", "\n"
                }

        }

}
