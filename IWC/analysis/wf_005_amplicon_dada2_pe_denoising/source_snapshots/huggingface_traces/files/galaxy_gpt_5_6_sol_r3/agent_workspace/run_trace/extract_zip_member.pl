use strict;
use warnings;
use IO::Uncompress::Unzip qw($UnzipError);

my ($archive, $member_suffix, $output) = @ARGV;
my $zip = IO::Uncompress::Unzip->new($archive)
    or die "Cannot open $archive: $UnzipError\n";

for (;;) {
    my $name = $zip->getHeaderInfo()->{Name};
    if ($name =~ /\Q$member_suffix\E$/) {
        open my $out, '>:raw', $output or die "Cannot write $output: $!\n";
        my $buffer;
        while ($zip->read($buffer) > 0) {
            print {$out} $buffer;
        }
        close $out;
        exit 0;
    }
    last unless $zip->nextStream();
}

die "Member ending in $member_suffix not found in $archive\n";
