import os


def test_jobscript_ont(tmp_path, run_jobscript):
    run_jobscript(
        input_filename="/repo/data/ARTIC/ERR5284916.ONT.ARTICv3.40k.fastq.gz",
        instrument_vendor="Oxford Nanopore",
    )

    assert os.path.exists(tmp_path / "report.pdf")


def test_jobscript_illumina(tmp_path, run_snp_mutator, run_art, run_jobscript):
    # generate some data
    run_snp_mutator(input_fasta_file="reference/nCoV-2019.reference.fasta", num_subs=3)
    run_art(coverage=15)
    run_jobscript(input_filename="simulated_reads.fastq.gz")

    assert os.path.exists(tmp_path / "report.pdf")