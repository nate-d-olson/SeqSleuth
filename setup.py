from setuptools import setup, find_packages

setup(
    name="seqsleuth",
    version="0.1.0",
    description="Metadata Extraction from FASTQ files",
    author="ND Olson",
    author_email="nolson@nist.gov",
    packages=find_packages(),
    install_requires=[
        "pysam",  # Add other dependencies here
    ],
)
