"""
Metadata Extraction from FASTQ files

This script allows the user to predict the sequencing technology and extract metadata from FASTQ files. 
The user can specify a list of FASTQ files as arguments. The output file name for the CSV output can also be specified. 
If not provided, the output file name defaults to 'output.csv'.

Usage: python main.py <FASTQ_files> [--num_reads] [--output] [--verbose] [--workers]

Required arguments:
    <FASTQ_files>: List of FASTQ files.

Optional arguments:
    --num_reads: Number of reads to process. Default is 5. Set to -1 to process all reads.
    --workers: Number of worker threads. Default is 1. Set to 'all' to use all CPU cores.
    --output: Output CSV file. Default is 'output.csv'.
    --verbose: If set, the script will print detailed messages.

Author: ND Olson
Date: 2023-05-12

Acknowledgements:
This script was developed with assistance from a conversation with OpenAI's ChatGPT.
"""

import argparse
import json
import csv
import os
import re
import logging
import sys
import multiprocessing
from urllib.parse import urlparse
from predict_tech_from_fastq import (
    FastqRecordReader,
    FastqFile,
    predict_sequencing_tech,
)
from extract_metadata import MetadataExtractor


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def main(fastq_files, args):
    """
    Main function that processes each FASTQ file and extracts metadata.
    """
    # Initialize CSV file for writing results
    with open(args.output, "w", newline="") as csvfile:
        fieldnames = ["filename", "predicted_tech", "metadata"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over fastq files
        for filename in fastq_files:
            # Initialize FastqRecordReader and predict sequencing technology
            reader = FastqRecordReader(filename, args.num_reads)
            fastq_file = FastqFile(reader, filename)

            predicted_tech = predict_sequencing_tech(filename, args.num_reads)
            logging.debug(f"Predicted technology for {filename}: {predicted_tech}")

            # Extract metadata
            if predicted_tech == "Unknown":
                metadata = {"Warning": "Unknown technology."}
            else:
                extractor = MetadataExtractor(fastq_file, filename, predicted_tech)
                metadata = extractor.extract_metadata(n_workers=args.workers)

            logging.debug(f"Metadata extracted for {filename}: {metadata}")

            # Write to CSV
            writer.writerow(
                {
                    "filename": filename,
                    "predicted_tech": predicted_tech,
                    "metadata": json.dumps(metadata),
                }
            )


def validate_num_reads(value):
    """
    Validate num_reads argument.
    """
    ivalue = int(value)
    if ivalue <= -2 or ivalue == 0:
        raise argparse.ArgumentTypeError(
            "Please provide a number greater than 0 for the number of reads "
            + "to analyze, or -1 to analyze all"
        )
    return ivalue


def validate_workers(value):
    """
    Validate workers argument.
    """
    if value == "all":
        return multiprocessing.cpu_count()
    else:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                "Number of workers must be greater than 0, or 'all' to use all CPU cores."
            )
        return ivalue


if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Predict the technology and extract metadata from fastq files."
    )

    # Define arguments
    parser.add_argument("fastq_files", type=str, nargs="*", help="List of fastq files.")
    parser.add_argument(
        "--num_reads",
        type=validate_num_reads,
        default=5,
        help="Number of reads to process. Defaults to 5. Set to -1 to process all reads.",
    )
    parser.add_argument(
        "--workers",
        type=validate_workers,
        default=1,
        help="Number of worker threads. Defaults to 1. Set to 'all' to use all CPU cores.",
    )
    parser.add_argument(
        "--output", type=str, default="output.csv", help="Output CSV file."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed messages."
    )

    # Parse arguments
    args = parser.parse_args()

    # Change level to DEBUG if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle fastq_files or file_list arguments
    if args.file_list:
        with open(args.file_list, "r") as f:
            fastq_files = [line.strip() for line in f]
    else:
        fastq_files = args.fastq_files

    # Check if fastq_files exist and are of correct format (.fastq)
    for file in fastq_files:
        parsed = urlparse(file)
        if bool(parsed.netloc):  # This is a URL
            if not re.match(r".*\.(fastq|fq)(\.gz)?$", parsed.path):
                parser.error(
                    f"The file {file} is not a fastq file based on file extension! "
                    "Expected .fastq, .fastq.gz, .fq, or .fq.gz."
                )
        else:  # This is a local file
            if (
                not file.endswith(".fastq")
                and not file.endswith(".fastq.gz")
                and not file.endswith(".fq")
                and not file.endswith(".fq.gz")
            ):
                parser.error(
                    f"The file {file} is not a fastq file based on file extension! "
                    "Expected .fastq, .fastq.gz, .fq, or .fq.gz."
                )
            elif not os.path.exists(file):
                parser.error(f"The file {file} does not exist!")

    # Execute main function
    main(fastq_files, args)
