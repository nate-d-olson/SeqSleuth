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
pip install -r requirements.txt
```

### Usage

The primary script for this package is `main.py`. It takes a list of Fastq files as arguments, and outputs the extracted metadata to a CSV file.

Basic usage is as follows:

```bash
python main.py <FASTQ_files> [--chunk_size] [--output] [--verbose] [--workers]
```

#### Arguments

* `<FASTQ_files>`: List of Fastq files.
* `--chunk_size`: Size of file chunk to read (in GB). Default is 1.
* `--output`: Output CSV file. Default is 'output.csv'.
* `--verbose`: If set, the script will print detailed messages.
* `--workers`: Number of worker threads. Defaults to 1. Set to 'all' to use all CPU cores.

## Contributing

We are not currently accepting contributions from the community, as the package is being developed specifically for the GIAB project. However, we welcome feedback and suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* This script was developed with assistance from a conversation with OpenAI's ChatGPT.