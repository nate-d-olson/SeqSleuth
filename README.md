# SeqSleuth

SeqSleuth is a Python package developed for the Genome in a Bottle (GIAB) data portal. It's purpose is to collect and organize metadata from Fastq, bam, 
and vcf files for further usage and analysis. 
The primary goal of this project is to streamline and automate the metadata extraction and processing workflow for the GIAB project.

While we are open to re-use or modification of the code by the community, 
please note that the package is currently being developed with the specific use-case of the GIAB project in mind. 
Therefore, functionality required for other projects may not be provided or may require adaptation of the existing code.

## Features

* Extracts metadata from fastq, bam, and vcf files based on file url and file contents.
* Outputs the extracted metadata to a CSV file for easy review and further processing
* Supports multi-threading to speed up metadata extraction from large batches of files

## Getting Started

### Prerequisites

This package requires Python 3.7 or newer.

### Installation

Clone this repository to your local machine and navigate to the project root directory.

Run the following command to install the necessary dependencies:

```bash
pip install .
```

### Usage

The primary script for this package is `main.py`. It takes a list of Fastq files as arguments, and outputs the extracted metadata to a CSV file.

Basic usage is as follows:

```bash
usage: seqsleuth [-h] [--num_reads NUM_READS] [--workers WORKERS] [--output_dir OUTPUT_DIR] [--verbose] [--progress] [--version] file_list

Predict the technology and extract metadata from fastq, bam, and vcf files.

positional arguments:
  file_list             A csv file containing a the columns `file_type`, `filename`, and `filepath`. The `filename` and `filepath` values are combined to generate the file url, assuming the file is
                        on the NIH hosted GIAB ftp site.

options:
  -h, --help            show this help message and exit
  --num_reads NUM_READS
                        Number of reads to process. Defaults to 5. Set to -1 to process all reads.
  --workers WORKERS     Number of worker threads. Defaults to 1. Set to 'all' to use all CPU cores.
  --output_dir OUTPUT_DIR
                        Output directory.
  --verbose             Print detailed messages.
  --progress            Show progress bar.
  --version             show program's version number and exit
```


## Contributing

We are not currently accepting contributions from the community, as the package is being developed specifically for the GIAB project. However, we welcome feedback and suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* This script was developed with assistance from a conversation with OpenAI's ChatGPT.


.
├── __init__.py
├── config.py: module with program configuation
├── extractors
│   ├── __init__.py
│   ├── bam.py: module to extract metadata from bam headers
│   ├── readnames.py: module to extract metadata from read names (depends on seqtech.py)
│   ├── seqtech.py: module with classes for use in extracting metadata from read names
│   └── vcf.py: module to extract metadata from vcf headers
├── keywords
│   ├── __init__.py
│   ├── _centers.py: dictionary with keywords for centers contributing analyses and performing sequencing
│   ├── _samps.py: dictionary with keywords for samples
│   ├── _seqtech.py: dictionary with keywords for different sequencing technology
│   ├── bam.py: metadata keywords for parsing bam filenames
│   ├── fastq.py: metadata keywords for parsing fastq filenames
│   └── vcf.py: metadata keywords for parsing vcf file names
├── main.py: entry point for program, currently only for fastq functionality
├── parser_filename.py: module for extracting metadata based on keywords from filenames/ paths
├── predict_tech_from_fastq.py: fastq specific code to predict the type of sequencing data used to generate a fastq file, includes classes for reading and extracting read names from fastq files
└── utils.py: utility functions used in multiple modules