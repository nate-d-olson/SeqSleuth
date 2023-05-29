"""
Extracts metadata from URLs and writes the metadata to a CSV file.
This script can be run from the command line and accepts either a single URL
or a file containing a list of URLs as input.

The script requires a JSON file with metadata keywords or a preset list name.

Usage:
    python extract_metadata.py -u URL -k keywords.json -c config.json -o output.csv
    OR
    python extract_metadata.py -f url_file.txt -k keywords.json -c config.json -o output.csv
"""

import argparse
import json
import logging
import re
import urllib.parse
from importlib import import_module
from typing import List, Dict

import pandas as pd

import config as cfg


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Extract metadata from URLs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help="A single URL to process.")
    group.add_argument('-f', '--url_file', help="A file containing a list of URLs.")
    parser.add_argument('-o', '--output', required=True, help="Output file to write metadata to.")
    parser.add_argument('-k', '--keywords', required=True, help="Keyword metadata JSON file or preset list name.")
    parser.add_argument('-c', '--config', required=True, help="Configuration file.")
    return parser.parse_args()


def setup_logger() -> None:
    """
    Set up the logger using the logging level from the configuration file.
    """
    numeric_level = getattr(logging, cfg.LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {cfg.LOG_LEVEL}')
    logging.basicConfig(level=numeric_level)

def validate_url(url: str) -> bool:
    """
    Validate a URL if URL validation is enabled in the configuration file.
    """
    if cfg.VALIDATE_URL:
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    else:
        return True

def load_urls(url: str) -> List[str]:
    """
    Load URLs from a text file.

    Args:
        url_file: Path to a text file containing URLs.

    Returns:
        A list of URLs.
    """
    with open(url, 'r') as file:
        urls = file.read().splitlines()
    return urls


def load_keywords(keywords: str) -> Dict:
    """
    Load keyword metadata from a JSON file or one of the preset lists.

    Args:
        keywords: Path to a JSON file or name of a preset list.

    Returns:
        A dictionary containing the keyword metadata.
    """
    if keywords in cfg.KEYWORD_LISTS:
        # Load from the preset lists
        keywords_module = import_module(f"keywords.{keywords}")
        return keywords_module.metadata_keywords
    else:
        # Load from a JSON file
        with open(keywords, 'r') as file:
            return json.load(file)


def replace_special_characters_with_spaces(text: str) -> str:
    """
    Replace special characters with spaces.

    Args:
        text: Text to process.

    Returns:
        Text with special characters replaced by spaces.
    """
    pattern = r'[^a-zA-Z0-9\s]'
    processed_text = re.sub(pattern, ' ', text)
    return processed_text

def prepare_keywords(metadata_keywords: dict) -> dict:
    """
    Prepare a mapping of keywords to categories for quick lookup.
    
    Args:
        metadata_keywords: Dictionary of categories and associated keywords.
    
    Returns:
        A dictionary with keywords as keys and categories as values.
    """
    keyword_map = {}
    for category, keywords in metadata_keywords.items():
        for key, values in keywords.items():
            for value in values:
                keyword_map[value] = (category, key)
    return keyword_map


def extract_metadata_from_url(url: str, keyword_map: dict, date_patterns: list) -> dict:
    """
    Extract metadata from a URL.

    Args:
        url: A string containing the URL to process.
        keyword_map: A dictionary containing a mapping of keywords to categories.
        date_patterns: A list of date pattern strings.

    Returns:
        A dictionary with extracted metadata.
    """
    metadata = {}
    parsed_url = urllib.parse.urlparse(url).path.split('/')
    # Extract metadata based on keywords
    matches = []
    for i, part in reversed(list(enumerate(parsed_url))):  # start searching from the end
        part = part.lower()
        if part in keyword_map:
            category, key = keyword_map[part]
            matches.append((i, key))  # store both position and keyword
            if category not in metadata:  # only update if category not already set
                metadata[category] = matches[0][1]  # select the keyword that appears last

    # Extract dates from the URL
    for part in reversed(parsed_url):
        if 'date' in metadata:
            break
        part = replace_special_characters_with_spaces(part)
        for pattern in date_patterns:
            match = re.search(pattern, part)
            if match:
                metadata['date'] = match.group()
                break

    metadata['url'] = url
    return metadata


def write_output(metadata: pd.DataFrame, output: str) -> None:
    """
    Write metadata to a CSV file.

    Args:
        metadata: pandas DataFrame containing the extracted metadata.
        output: Path to the output CSV file.
    """
    metadata.to_csv(output, index=False)


def main() -> None:
    """
    The main function that runs the script.
    """
    args = parse_args()
    setup_logger()
    urls = [args.url] if args.url else load_urls(args.url_file)
    
    # Load the metadata keywords from the specified source.
    metadata_keywords = load_keywords(args.keywords)
    keyword_map = prepare_keywords(metadata_keywords)
    
    # Extract metadata from the URLs
    for url in urls:
        if not validate_url(url):
            logging.error(f'Invalid URL: {url}')
            continue
        try
        metadata = extract_metadata_from_url(url, keyword_map)
    write_output(metadata, args.output)


if __name__ == "__main__":
    main()
