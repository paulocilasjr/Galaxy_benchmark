use strict;
use warnings;
use IO::Uncompress::Unzip qw($UnzipError);
use JSON::PP qw(decode_json);

my ($counts_path, $reps_qza, $collection_json, $output_path) = @ARGV;
die "usage: $0 counts.tsv reps.qza collection.json output.tsv\n" unless defined $output_path;

open my $cfh, '<', $collection_json or die "open $collection_json: $!";
my $collection;
{
    local $/;
    $collection = decode_json(<$cfh>);
}
close $cfh;
my @expected = map { $_->{element_identifier} } @{$collection->{elements}};
die "expected 17 samples, found " . scalar(@expected) . "\n" unless @expected == 17;

my $zip = IO::Uncompress::Unzip->new($reps_qza)
    or die "open $reps_qza: $UnzipError\n";
my $fasta = '';
for (my $more = 1; $more > 0; $more = $zip->nextStream()) {
    my $name = $zip->getHeaderInfo()->{Name} // '';
    next unless $name =~ m{/data/[^/]+\.fasta$};
    my $buffer;
    while (($zip->read($buffer)) > 0) {
        $fasta .= $buffer;
    }
}
die "representative-sequence FASTA not found in $reps_qza\n" unless length $fasta;

my %sequence_for;
my $id;
for my $line (split /\r?\n/, $fasta) {
    if ($line =~ /^>(\S+)/) {
        $id = $1;
        die "duplicate FASTA identifier $id\n" if exists $sequence_for{$id};
        $sequence_for{$id} = '';
    } elsif (length $line) {
        die "sequence before FASTA identifier\n" unless defined $id;
        $line =~ s/\s+//g;
        $sequence_for{$id} .= uc $line;
    }
}

open my $tfh, '<', $counts_path or die "open $counts_path: $!";
open my $out, '>', $output_path or die "open $output_path: $!";
my @samples;
my %seen_sequence;
my $rows = 0;
while (my $line = <$tfh>) {
    $line =~ s/\r?\n$//;
    next if $line eq '# Constructed from biom file';
    if (!@samples) {
        my @header = split /\t/, $line, -1;
        die "unexpected BIOM TSV header\n" unless shift(@header) eq '#OTU ID';
        @samples = @header;
        my %expected = map { $_ => 1 } @expected;
        my %observed = map { $_ => 1 } @samples;
        die "sample count is not 17\n" unless @samples == 17;
        die "sample identifiers differ from supplied collection\n"
            unless join("\0", sort keys %expected) eq join("\0", sort keys %observed);
        print {$out} join("\t", 'sequence', @samples), "\n";
        next;
    }
    next unless length $line;
    my @fields = split /\t/, $line, -1;
    my $feature = shift @fields;
    die "wrong number of counts for $feature\n" unless @fields == @samples;
    my $sequence = $sequence_for{$feature};
    die "missing sequence for feature $feature\n" unless defined $sequence;
    die "invalid ASV sequence for $feature\n" unless $sequence =~ /^[ACGT]+$/;
    die "duplicate ASV sequence\n" if $seen_sequence{$sequence}++;
    my @counts;
    for my $value (@fields) {
        die "invalid count '$value' for $feature\n" unless $value =~ /^\d+(?:\.0+)?$/;
        my $count = int($value);
        die "negative count for $feature\n" if $count < 0;
        push @counts, $count;
    }
    print {$out} join("\t", $sequence, @counts), "\n";
    $rows++;
}
close $tfh;
close $out;
die "no table header found\n" unless @samples;
die "feature/sequence count mismatch: table=$rows fasta=" . scalar(keys %sequence_for) . "\n"
    unless $rows == keys %sequence_for;
print "samples=" . scalar(@samples) . " asvs=$rows\n";
