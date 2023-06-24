import pytest
import os
import csv
from seqsleuth import main, version
from seqsleuth.extractors.bam import BAMMetadataExtractor
from seqsleuth.extractors.filename import FilenameMetadataExtractor
from seqsleuth.extractors.readnames import ReadNameMetadataExtractor
from seqsleuth.extractors.vcf import VCFMetadataExtractor
from seqsleuth.predict_tech_from_fastq import predict_sequencing_tech


@pytest.fixture
def sample_fastq_file(tmpdir):
    # Create a temporary FASTQ file for testing predict_sequencing_tech()
    fastq_file = tmpdir.join("sample.fastq")
    fastq_file.write(
        '@read1\nAGCTCGTAGCTACGTA\n+\nHHHHHHHHHHHHHHHH\n@read2\nTCAGCTAGCTAGC\n+\nHHHHHHHHHHH'
    )
    return str(fastq_file)


def test_predict_sequencing_tech(sample_fastq_file):
    # Test predict_sequencing_tech()
    tech = predict_sequencing_tech(sample_fastq_file)
    assert tech == "Illumina"


def test_bam_metadata_extractor():
    # Test BAMMetadataExtractor
    bam_file = "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/analysis/10XGenomics_ChromiumGenome_LongRanger2.0_06202016/HG002_NA24385_son/NA24385_GRCh37.bam"
    extractor = BAMMetadataExtractor(bam_file)
    metadata = extractor.extract_metadata()
    assert metadata == {
        "url": bam_file,
        "header": {},
        "first_read_name": None,
    }


def test_filename_metadata_extractor():
    # Test FilenameMetadataExtractor
    metadata_keywords = {
        "category1": {"keyword1": ["kw1", "kw_one"], "keyword2": ["kw2", "kw_two"]},
        "category2": {"keyword3": ["kw3"]},
    }
    extractor = FilenameMetadataExtractor(metadata_keywords)
    filename = "/path/to/my_file_kw1_kw3.txt"
    metadata = extractor.extract_metadata(filename)
    assert metadata == {
        "filename": filename,
        "category1": "keyword1",
        "category2": "keyword3",
    }


def test_vcf_metadata_extractor(tmpdir):
    # Test VCFMetadataExtractor
    vcf_file = tmpdir.join("sample.vcf")
    vcf_file.write("#fileformat=VCFv4.3\n##INFO=<ID=DP,Number=1,Type=Integer,Description=\"Total Depth\">\n")
    extractor = VCFMetadataExtractor(str(vcf_file))
    metadata = extractor.extract_metadata()
    assert metadata == {
        "url": str(vcf_file),
        "header": {
            "fileformat": "VCFv4.3",
            "samples": [],
            "INFO": [
                {"ID": "DP", "Number": "1", "Type": "Integer", "Description": "Total Depth"}
            ],
        },
    }


def test_version():
    # Test the version module
    assert version.__version__ == "0.2.0"


# Add more tests as needed