use strict;
use warnings;

my ($fasta_path, $counts_path) = @ARGV;
my @samples = qw(
    mFMT_cecal_1191_2 mFMT_cecal_1191_3 mFMT_cecal_1275_1
    mFMT_cecal_1275_2 mFMT_cecal_1275_4 hFMT_cecal_1296_1
    hFMT_cecal_1296_2 hFMT_cecal_1296_3 hFMT_cecal_1297_1
    hFMT_cecal_1297_2 hFMT_cecal_1297_4 noFMT_cecal_1192_1
    noFMT_cecal_1192_3 noFMT_cecal_1294_1 noFMT_cecal_1294_2
    noFMT_cecal_1294_3 noFMT_cecal_1295_4
);

open my $fasta, '<', $fasta_path or die "Cannot read $fasta_path: $!\n";
my (%sequence_for, $id);
while (my $line = <$fasta>) {
    $line =~ s/\r?\n$//;
    if ($line =~ /^>(\S+)/) {
        $id = $1;
        die "Duplicate FASTA identifier: $id\n" if exists $sequence_for{$id};
        $sequence_for{$id} = '';
    } else {
        die "Sequence before FASTA identifier\n" unless defined $id;
        $sequence_for{$id} .= uc $line;
    }
}
close $fasta;

open my $counts, '<', $counts_path or die "Cannot read $counts_path: $!\n";
my (@source_header, %source_column);
while (my $line = <$counts>) {
    $line =~ s/\r?\n$//;
    next if $line eq '# Constructed from biom file';
    if (!@source_header) {
        @source_header = split /\t/, $line, -1;
        die "Unexpected BIOM TSV identifier header\n" unless $source_header[0] eq '#OTU ID';
        for my $index (1 .. $#source_header) {
            die "Duplicate sample column: $source_header[$index]\n"
                if exists $source_column{$source_header[$index]};
            $source_column{$source_header[$index]} = $index;
        }
        for my $sample (@samples) {
            die "Missing sample column: $sample\n" unless exists $source_column{$sample};
        }
        die "Unexpected sample-column count\n" unless keys(%source_column) == @samples;
        print join("\t", 'sequence', @samples), "\n";
        next;
    }

    my @fields = split /\t/, $line, -1;
    my $feature_id = $fields[0];
    die "Missing sequence for feature $feature_id\n" unless exists $sequence_for{$feature_id};
    my $sequence = $sequence_for{$feature_id};
    die "Invalid ASV sequence for $feature_id\n" unless $sequence =~ /^[ACGT]+$/;

    my @raw_counts;
    for my $sample (@samples) {
        my $value = $fields[$source_column{$sample}];
        die "Non-integer count for $feature_id/$sample: $value\n"
            unless defined $value && $value =~ /^\d+(?:\.0+)?$/;
        $value =~ s/\.0+$//;
        push @raw_counts, $value;
    }
    print join("\t", $sequence, @raw_counts), "\n";
    delete $sequence_for{$feature_id};
}
close $counts;

die "Feature sequences absent from count table\n" if keys %sequence_for;
