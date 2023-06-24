import argparse
import json
import logging
import os
from typing import Any, Dict, List


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


def write_json_to_file(data: List[Dict[str, Any]], filename: str) -> None:
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
