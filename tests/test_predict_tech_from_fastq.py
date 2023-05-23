import pytest
import pysam
from seqsleuth.predict_tech_from_fastq import (
    FastqRecordReader,
    TechnologyPredictor,
    FastqFile,
    predict_sequencing_tech,
    TECH_ILLUMINA,
    TECH_PACBIO,
    TECH_OXFORDNANOPORE,
    TECH_UNKNOWN,
    MAX_LENGTH_SHORT_READ,
    TECH_IDENTIFIERS,
)


def test_FastqRecordReader_reads_correct_number_of_records():
    # You'll need a FASTQ file with at least 10 records for this test
    filename = "test_data/test_ill.fastq.gz"
    reader = FastqRecordReader(filename, 4)
    records = list(reader.read_records())
    assert len(records) == 4


def test_FastqFile_gets_read_names():
    # You'll need a FASTQ file for this test
    filename = "test_data/test_ont.fastq.gz"
    reader = FastqRecordReader(filename, 4)
    records = list(reader.read_records())
    fastq_file = FastqFile(records, filename)
    assert len(fastq_file.read_names) == 4


def test_predict_sequencing_tech():
    # You'll need a FASTQ file named in a way that indicates the sequencing technology for this test
    filename = "test_data/test_pacbio.fastq.gz"
    tech = predict_sequencing_tech(filename)
    assert tech is not None


#### Tests using mocker ########################################################
## Not yet implemented, need to debug first
# Mock pysam.FastxRecord object
class MockFastxRecord:
    def __init__(self, name, sequence, comment=None):
        self.name = name
        self.sequence = sequence
        self.comment = comment


# def test_FastqRecordReader(mocker):
#     mocker.patch('pysam.FastxFile', return_value=[MockFastxRecord("name1", "sequence1")] * 10)
#     reader = FastqRecordReader("test_data/test_ill.fastq.gz", 4)
#     records = list(reader.read_records())
#     assert len(records) == 4

# def test_TechnologyPredictor_is_short_read_technology():
#     record_short = MockFastxRecord("name1", "sequence1" * (MAX_LENGTH_SHORT_READ - 1))
#     record_long = MockFastxRecord("name2", "sequence2" * MAX_LENGTH_SHORT_READ)
#     predictor = TechnologyPredictor()

#     predictor.records = [record_short]
#     assert predictor.is_short_read_technology() is True

#     predictor.records = [record_long]
#     assert predictor.is_short_read_technology() is False

# def test_TechnologyPredictor_predict_technology_based_on_read_names():
#     predictor = TechnologyPredictor()
#     predictor.records = [MockFastxRecord("read1:1", "sequence1"), MockFastxRecord("mread2", "sequence2"), MockFastxRecord("cread3", "sequence3")]
#     assert predictor.predict_technology_based_on_read_names() == TECH_ILLUMINA

#     predictor.records = [MockFastxRecord("mread1", "sequence1"), MockFastxRecord("cread2", "sequence2")]
#     assert predictor.predict_technology_based_on_read_names() == TECH_PACBIO

#     predictor.records = [MockFastxRecord("read1", "sequence1")]
#     assert predictor.predict_technology_based_on_read_names() == TECH_OXFORDNANOPORE

#     predictor.records = [MockFastxRecord("otherread1", "sequence1")]
#     assert predictor.predict_technology_based_on_read_names() == TECH_UNKNOWN

# def test_FastqFile_predict_technology_based_on_filename():
#     records = [MockFastxRecord("name1", "sequence1")]
#     for tech, identifiers in TECH_IDENTIFIERS.items():
#         for identifier in identifiers:
#             fastq_file = FastqFile(records, f"test_data/test_{identifier}.fastq")
#             assert fastq_file.predict_technology_based_on_filename() == tech

#     fastq_file = FastqFile(records, "test.fastq")
#     assert fastq_file.predict_technology_based_on_filename() == TECH_UNKNOWN

# def test_predict_sequencing_tech(mocker):
#     mocker.patch('pysam.FastxFile', return_value=[MockFastxRecord("name1", "sequence1")] * 10)
#     for tech, identifiers in TECH_IDENTIFIERS.items():
#         for identifier in identifiers:
#             assert predict_sequencing_tech(f"test_data/test_{identifier}.fastq", 10) == tech

#     assert predict_sequencing_tech("test_data/test.fastq", 10) == TECH_UNKNOWN
