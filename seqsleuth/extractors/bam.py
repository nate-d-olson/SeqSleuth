"""
bam_to_json.py

This script was developed in collaboration with OpenAI's GPT-3 model, as of September 2021.

It takes a list of URLs pointing to BAM files and generates a JSON file containing header information from each BAM file, 
along with the name of the first read in the file. The list of URLs is read from a file, with one URL per line.

Usage:
    python bam_to_json.py --urls_file urls.txt --output_file output.json

Where:
    urls.txt is a text file with one URL per line
    output.json is the desired name of the output JSON file

Note: This script requires the pysam Python package.
"""

import argparse
import logging
import pysam
import json
import os
from typing import List, Optional, Dict, Any


import pysam

class BAMMetadataExtractor:
    def __init__(self, filepath):
        self.filepath = filepath

    def extract_metadata(self):
        metadata = {}
        
        # Open the BAM file
        with pysam.AlignmentFile(self.filepath, "rb") as bam_file:

            # Extract some basic metadata
            metadata["mapped_reads"] = bam_file.mapped
            metadata["unmapped_reads"] = bam_file.unmapped
            metadata["n_references"] = bam_file.nreferences
            metadata["references"] = bam_file.references
            metadata["lengths"] = bam_file.lengths
            metadata["is_sorted"] = bam_file.is_sorted

            # This is just an example. 
            # You could extract any other relevant information from the BAM file

        return metadata


def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )


def valid_file(file_path: str) -> str:
    """Validate that the file exists.

    Args:
        file_path: The path to the file.

    Returns:
        The file path, if the file exists.

    Raises:
        argparse.ArgumentTypeError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise argparse.ArgumentTypeError(f"The file {file_path} does not exist!")
    return file_path


def get_bam_info(url: str) -> Optional[Dict[str, Any]]:
    """Get header information and first read name from a BAM file.

    Args:
        url: The URL of the BAM file.

    Returns:
        A dictionary with the BAM file header information and the first read name, or None if an error occurred.
    """
    try:
        bamfile = pysam.AlignmentFile(url, "rb")

        # Get the header as a dictionary
        header_dict = bamfile.header.to_dict()

        # Get the name of the first read
        first_read_name = next(bamfile).query_name

        bamfile.close()

        # Add the first read name and url to the header dictionary
        header_dict["first_read_name"] = first_read_name
        header_dict["url"] = url

        return header_dict

    except Exception as e:
        logging.error(f"Failed to process BAM file at {url}. Error: {str(e)}")
        return {"url": url, "error": str(e)}


def bam_to_json(urls: List[str]) -> List[Dict[str, Any]]:
    """Get information from a list of BAM files.

    Args:
        urls: A list of URLs of the BAM files.

    Returns:
        A list of dictionaries with the BAM file information.
    """
    output = []

    for url in urls:
        info = get_bam_info(url)
        if info is not None:
            output.append(info)

    return output


def write_to_file(data: List[Dict[str, Any]], filename: str) -> None:
    """Write the data to a JSON file.

    Args:
        data: The data to write to the file.
        filename: The name of the file to write to.
    """
    try:
        with open(filename, "w") as outfile:
            json.dump(data, outfile)
    except Exception as e:
        logging.error(f"Failed to write to output file {filename}. Error: {str(e)}")


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(description="Process a list of URLs to BAM files.")
    parser.add_argument(
        "--urls_file",
        type=valid_file,
        required=True,
        help="File containing a list of URLs",
    )

    parser.add_argument(
        "--output_file", type=str, required=True, help="Name of the output JSON file."
    )

    args = parser.parse_args()

    try:
        with open(args.urls_file, "r") as f:
            urls = [line.strip() for line in f]
    except Exception as e:
        logging.error(
            f"Failed to read URLs from input file {args.urls_file}. Error: {str(e)}"
        )
        exit(1)

    data = bam_to_json(urls)
    write_to_file(data, args.output_file)
