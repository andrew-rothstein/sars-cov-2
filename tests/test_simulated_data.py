from Bio import SeqIO
import pandas as pd
import pytest


@pytest.mark.parametrize("n", [x for x in range(1, 2)])
def test_snps_only_fastq(
    tmp_path, n, run_art, run_jobscript, run_snp_mutator, read_vcf_as_dataframe
):
    """Tests insert of N snps"""
    run_snp_mutator(
        input_fasta_file="reference/nCoV-2019.reference.fasta",
        num_subs=n,
        num_insertions=5,
        num_deletions=5,
    )

    # Run ART
    run_art()

    # Run pipeline on simulated data
    run_jobscript(input_filename="simulated_reads.fastq.gz")

    # Check that all variants are detected and there are no extras
    truth = pd.read_csv(open(tmp_path / "summary.tsv"), sep="\t")
    called = read_vcf_as_dataframe(tmp_path / "variants.vcf")

    # We don't test for position with indels because vcf positions are shifted by 0-2 bases
    # from the base immediately preceding the actual indel, which is how programs like Nextclade
    # report indel positions.
    assert list(truth["OriginalBase"]) == list(called["REF"])
    assert list(truth["NewBase"]) == list(called["ALT"])

    # We add these tests to ensure we have a high percent of reads aligning
    # We simulate at 50x, so low end variants with coverage variability should
    # be ~25-30x, and then another ~33-50% due to Q scores <20
    assert (called["ALT_DP"] > 10).all()
    assert called["ALT_DP"].mean() > 15

    # Finally, test that the FASTAs match
    # Note we ignore the first 50bp which may have low coverage and N masking
    # plus the final 120bps due to a polyA tail
    reference = list(SeqIO.parse(f"{tmp_path}/nCoV-2019.reference_mutated_1.fasta", "fasta"))[0]
    consensus = list(SeqIO.parse(f"{tmp_path}/consensus.fa", "fasta"))[0]
    assert consensus.seq[50:-120] in reference.seq
