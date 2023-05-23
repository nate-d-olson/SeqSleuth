"""
Metadata Extraction from FASTQ files

This script allows the user to predict the sequencing technology and extract metadata from FASTQ files. 
The user can specify a list of FASTQ files as arguments. The chunk size for reading the file and the 
output file name for the CSV output can also be specified. If not provided, the chunk size defaults to 
1 GB and the output file name defaults to 'output.csv'.

Usage: python main.py <FASTQ_files> [--chunk_size] [--output] [--verbose]

Required arguments:
    <FASTQ_files>: List of FASTQ files.

Optional arguments:
    --chunk_size: Size of file chunk to read (in GB). Default is 1.
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
from urllib.parse import urlparse
from predict_tech_from_fastq import (
    FastqRecordReader,
    FastqFile,
    predict_sequencing_tech,
)
from extract_metadata import MetadataExtractor


def main(fastq_files, args):
    ## Output CSV file
    with open(args.output, "w", newline="") as csvfile:
        fieldnames = ["filename", "predicted_tech", "metadata"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over fastq files
        for filename in fastq_files:
            ## Initialize FastqRecordReader and predict sequencing technology
            reader = FastqRecordReader(filename, args.num_reads)
            fastq_file = FastqFile(reader, filename)

            predicted_tech = predict_sequencing_tech(filename, args.num_reads)
            if args.verbose:
                print(f"Predicted technology for {filename}: {predicted_tech}")

            ## Extract metadata
            if predicted_tech == "Unknown":
                metadata = {"Warning": "Unknown technology."}
            else:
                extractor = MetadataExtractor(fastq_file, filename, predicted_tech)
                metadata = extractor.extract_metadata()

            if args.verbose:
                print(f"metadata extracted for {filename}: {metadata}")

            ## Write to CSV
            writer.writerow(
                {
                    "filename": filename,
                    "predicted_tech": predicted_tech,
                    "metadata": json.dumps(metadata),
                }
            )

def validate_num_reads(value):
    ivalue = int(value)
    if ivalue <= -2 or ivalue == 0:
        raise argparse.ArgumentTypeError(
            "Please provide a number greater than 0 for the number of reads " +
            "to analyze, or -1 to analyze all"
        )
    return ivalue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Predict the technology and extract metadata from fastq files."
    )

    parser.add_argument("fastq_files", type=str, nargs="*", help="List of fastq files.")
    parser.add_argument(
        "--file_list",
        type=str,
        help="A file containing a list of fastq files, one per line.",
    )
    parser.add_argument(
        "--num_reads",
        type=validate_num_reads,
        default=5,
        help="Number of reads to process. Defaults to 5. Set to -1 to process all reads.",
    )
    parser.add_argument(
        "--output", type=str, default="output.csv", help="Output CSV file."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed messages."
    )

    args = parser.parse_args()

    if args.file_list:
        with open(args.file_list, "r") as f:
            fastq_files = [line.strip() for line in f]
    else:
        fastq_files = args.fastq_files

    # Check if fastq_files exist and are of correct format (.fastq)
    for file in args.fastq_files:
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

    main(fastq_files, args)
