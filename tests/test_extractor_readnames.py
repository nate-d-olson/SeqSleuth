import pytest
from seqsleuth.extractors.seqtech import OxfordNanopore, PacBio, DovetailSeqTech

# Mocking the read_name for testing purposes
read_name_oxford = "..."
read_name_pacbio = "m64017_191118_150849/43322019/ccs"
read_name_dovetail = "..."

def test_oxford_nanopore_check_read_name_convention():
    oxford = OxfordNanopore()
    assert oxford.check_read_name_convention(read_name_oxford) == True

def test_pacbio_check_read_name_convention():
    pacbio = PacBio()
    assert pacbio.check_read_name_convention(read_name_pacbio) == True

def test_dovetail_check_read_name_convention():
    dovetail = DovetailSeqTech()
    assert dovetail.check_read_name_convention(read_name_dovetail) == True

def test_oxford_nanopore_extract_metadata_from_read():
    oxford = OxfordNanopore()
    metadata = oxford.extract_metadata_from_read(read_name_oxford)
    assert isinstance(metadata, dict)

def test_pacbio_extract_metadata_from_read():
    pacbio = PacBio()
    metadata = pacbio.extract_metadata_from_read(read_name_pacbio)
    assert isinstance(metadata, dict)

def test_dovetail_extract_metadata_from_read():
    dovetail = DovetailSeqTech()
    metadata = dovetail.extract_metadata_from_read(read_name_dovetail)
    assert isinstance(metadata, dict)
