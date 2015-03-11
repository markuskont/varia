#!/usr/bin/env perl


sub populateArrayFromFile {
	my ($filename) = @_;
	open FILE, $filename || die "Cannot open file ".$filename." for read";
	@lines=<FILE>;
	close FILE;
	return @lines;
}

sub ip6AppendZeroes {
	my ($address) = @_;
	@array = split(/:/, $address);
	my $address;
	
	foreach $elem (@array) {
		if (length $elem > 0 && length $elem < 4) {
			$elem = padWithZeroes($elem);
		} 
		elsif (length $elem == 0) {
			$elem = "::"
		} 
#		elsif (length $elem == 4) {
#			$elem = $elem
#		}
		$address = $address.$elem;
	}

	$address = ip6ConsecutiveHexFieldReplace($address);
	$address = ip6ReverseAndSeparate($address);
	return $address;
}

sub ip6ReverseAndSeparate {
	my ($address) = @_;
	$address = reverse $address;
	@octets = split(//, $address);

	foreach my $octet (@octets) {
		$octet = $octet."."
	}

	$address =~ s/(.)/$1\./g;

	return $address;
}

sub ip6ConsecutiveHexFieldReplace {
	my ($address) = @_;
	my $pad_len = 32 - length($address);
	my $find = "::";
	my $pad_len = $pad_len + 2;	# There is an offset, caused by "::" symbol taking up space

	$find = quotemeta $find;
	
	my $paddedNumber = "0" x ( $pad_len );

	$address =~ s/$find/$paddedNumber/g;

	return $address;
}

sub padWithZeroes {

	my ($number) = @_;
	my $pad_len = 4 - length($number);

	my $paddedNumber = "0" x ( $pad_len ) . $number;

	return $paddedNumber;

}

foreach my $filename (@ARGV) {

	my @newlines = ();
	my @lines = populateArrayFromFile($filename);
	
	foreach $line (@lines) {

		if ($line =~ m/([\dA-F:]+)\s+(\S+)/) {
			my $address = ip6AppendZeroes($1);
			print $address."ip6.arpa.		IN	PTR	$2.","\n"
		}

	}

}
