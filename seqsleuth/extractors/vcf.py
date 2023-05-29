"""
vcf_to_json.py

This script was developed in collaboration with OpenAI's GPT-3 model, as of September 2021.

It takes a list of URLs pointing to VCF files and generates a JSON file containing header information from each VCF file. 
The list of URLs is read from a file, with one URL per line.

Usage:
    python vcf_to_json.py --urls_file urls.txt --output_file output.json

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


def get_vcf_info(url: str) -> Optional[Dict[str, Any]]:
    """Get header information from a VCF file.

    Args:
        url: The URL of the VCF file.

    Returns:
        A dictionary with the VCF file header information, or None if an error occurred.
    """
    try:
        vcffile = pysam.VariantFile(url)
        # Get the header information
        header_fileformat = vcffile.header.version
        header_samples = list(vcffile.header.samples)

        # Add the header information to the dictionary
        header_dict = {
            "fileformat": header_fileformat, 
            "samples": header_samples,
        }
        
        # Initialize optional fields with None
        date, source, reference = None, None, None

        # Iterate over the header lines
        for record in vcffile.header.records:
            if record.key not in ['contig','INFO','FORMAT','FILTER']:
                header_dict[record.key] = record.value

        vcffile.close()

        return {'url': url, 'header': header_dict}

    except Exception as e:
        logging.error(f"Failed to process VCF file at {url}. Error: {str(e)}")
        return {'url': url, 'header': None, 'error': str(e)}



def vcf_to_json(urls: List[str]) -> List[Dict[str, Any]]:
    """Get information from a list of VCF files.

    Args:
        urls: A list of URLs of the VCF files.

    Returns:
        A list of dictionaries with the VCF file information.
    """
    output = []

    for url in urls:
        info = get_vcf_info(url)
        if info is not None:
            output.append(info)

    return output


def write_to_file(data: List[Dict[str, Any]], filename: str) -> None:
    """Write the data to a JSON file.

        Args:
            data: The data to# I will continue the script here as the previous message was cut off.

    ```python
            data: The data to write.
            filename: The name of the file to write to.
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Failed to write data to file {filename}. Error: {str(e)}")


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Process a list of URLs to VCF files and extract the headers into a JSON file."
    )

    parser.add_argument(
        "--urls_file",
        type=valid_file,
        required=True,
        help="A text file with one URL per line.",
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

    data = vcf_to_json(urls)
    write_to_file(data, args.output_file)
