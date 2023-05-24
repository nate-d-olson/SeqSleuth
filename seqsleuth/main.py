"""
Metadata Extraction from FASTQ files

This script allows the user to predict the sequencing technology and extract metadata from FASTQ files. 
The user can specify a list of FASTQ files as arguments. The output file name for the CSV output can also be specified. 
If not provided, the output file name defaults to 'output.csv'.

Usage: python main.py <FASTQ_files> [--num_reads] [--output] [--verbose] [--workers]

Required arguments:
    <FASTQ_files>: List of FASTQ files.

Optional arguments:
    --file_list: text file with a list of local file paths or uris for fastq files, assumes one file per row
    --num_reads: Number of reads to process. Default is 5. Set to -1 to process all reads.
    --workers: Number of worker threads. Default is 1. Set to 'all' to use all CPU cores.
    --output: Output CSV file. Default is 'output.csv'.
    --verbose: If set, the script will print detailed messages.
    --progress: If set, the script will provide a progress bar indicating the number of fastq files analyzed.

Author: ND Olson
Date: 2023-05-12

Acknowledgements:
This script was developed with assistance from a conversation with OpenAI's ChatGPT.
"""

import argparse
import concurrent.futures
import csv
import json
import logging
import os
import re
import sys
from multiprocessing import cpu_count
from typing import Any, Dict, List
from urllib.parse import urlparse

from extract_metadata import MetadataExtractor
from predict_tech_from_fastq import (
    FastqFile,
    FastqRecordReader,
    predict_sequencing_tech,
)
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def process_file(filename: str, num_reads: int) -> Dict[str, Any]:
    # Logging process id for debugging multiprocessing
    logging.debug(f"Processing file: {filename} in process id: {os.getpid()}")

    try:
        # Initialize FastqRecordReader and predict sequencing technology
        reader = FastqRecordReader(filename, num_reads)
        records = list(reader.read_records())
        fastq_file = FastqFile(records, filename)
        logging.debug(
            f"Initialized FastqRecordReader and FastqFile for file: {filename}"
        )

        predicted_tech = predict_sequencing_tech(filename, num_reads)
        logging.debug(f"Predicted technology for file {filename} is {predicted_tech}")

        # Extract metadata
        if predicted_tech == "Unknown":
            metadata = {"Warning": "Unknown technology."}
            logging.warning(
                f"Unknown technology for file {filename}. Unable to extract metadata."
            )
        else:
            extractor = MetadataExtractor(fastq_file, filename, predicted_tech)
            metadata = extractor.extract_metadata()  # multiprocessing.cpu_count())
            logging.debug(f"Extracted metadata for file: {filename}")

        # Output results
        return {
            "filename": filename,
            "predicted_tech": predicted_tech,
            "metadata": json.dumps(metadata),
        }

    except Exception as e:
        # If there's an error, log it and continue to the next file
        logging.error(f"Error processing file: {filename}. Error message: {str(e)}")
        pass


def main(fastq_files: List[str], args: argparse.Namespace) -> None:
    """
    Main function that processes each FASTQ file and extracts metadata.
    """
    # Initialize CSV file for writing results
    with open(args.output, "w", newline="") as csvfile:
        fieldnames = ["filename", "predicted_tech", "metadata"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Create a progress bar
        logging.info(f"Initiate processing of fastq files")
        pbar = tqdm(total=len(fastq_files), disable=not args.progress)

        # Initialize a ProcessPoolExecutor
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers
        ) as executor:
            # Prepare futures for all fastq files
            futures = {
                executor.submit(process_file, filename, args.num_reads): filename
                for filename in fastq_files
            }

            # Iterate over futures as they complete
            for future in concurrent.futures.as_completed(futures):
                # Get results from the future and write them to the CSV
                writer.writerow(future.result())

                # Update progress bar
                pbar.update(1)

        # Close the progress bar
        pbar.close()


def validate_num_reads(value: str) -> int:
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


def validate_workers(value: str) -> int:
    """
    Validate workers argument.
    """
    if value == "all":
        return cpu_count()
    else:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                "Number of workers must be greater than 0, or 'all' to use all CPU cores."
            )
        return ivalue


def validate_files(fastq_files: List[str], parser: argparse.ArgumentParser) -> None:
    """
    Validate the provided files for correct format and existence.
    """
    for file in fastq_files:
        parsed = urlparse(file)
        if bool(parsed.netloc):  # This is a URL
            if not re.match(r".*\.(fastq|fq)(\.gz)?$", parsed.path, re.IGNORECASE):
                parser.error(
                    f"The file {file} is not a fastq file based on file extension! "
                    "Expected .fastq, .fastq.gz, .fq, or .fq.gz."
                )
        else:  # This is a local file
            if (
                not file.lower().endswith(".fastq")
                and not file.lower().endswith(".fastq.gz")
                and not file.lower().endswith(".fq")
                and not file.lower().endswith(".fq.gz")
            ):
                parser.error(
                    f"The file {file} is not a fastq file based on file extension! "
                    "Expected .fastq, .fastq.gz, .fq, or .fq.gz."
                )
            elif not os.path.exists(file):
                parser.error(f"The file {file} does not exist!")


if __name__ == "__main__":
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Predict the technology and extract metadata from fastq files."
    )

    # Define arguments
    parser.add_argument("fastq_files", type=str, nargs="*", help="List of fastq files.")
    parser.add_argument(
        "--file_list",
        type=argparse.FileType("r"),
        help="A file containing a list of fastq files, one per line.",
    )
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
    parser.add_argument("--progress", action="store_true", help="Show progress bar.")

    # Parse arguments
    args = parser.parse_args()

    # Change level to DEBUG if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle fastq_files or file_list arguments
    if args.file_list:
        fastq_files = [line.strip() for line in args.file_list]
    else:
        fastq_files = [f.name for f in args.fastq_files]

    # Check if fastq_files exist and are of correct format (.fastq)
    validate_files(fastq_files, parser)

    # Execute main function
    main(fastq_files, args)
