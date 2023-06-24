import re
import urllib.parse
from typing import Dict, List, Any


class FilenameMetadataExtractor:
    """
    This class is used to extract metadata from a filename
    """

    def __init__(self, metadata_keywords: Dict[str, Dict[str, List[str]]]):
        """
        Initialize the extractor with a mapping of keywords to categories and date patterns.

        Args:
            metadata_keywords: A dictionary containing a mapping of keywords to categories.
            date_patterns: A list of date pattern strings.
        """
        assert isinstance(
            metadata_keywords, dict
        ), "metadata_keywords must be a dictionary"
        for category, keywords in metadata_keywords.items():
            assert isinstance(
                keywords, dict
            ), f"Each category in metadata_keywords must be a dictionary. Category '{category}' is not a dictionary. {keywords}"

        self.keyword_map = self.prepare_keywords(metadata_keywords)
        self.date_patterns = [
            r"\d{8}",  # YYYYMMDD
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}\d{4}",  # MMDDYYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
        ]

    @staticmethod
    def replace_special_characters_with_spaces(text: str) -> str:
        """
        Replace special characters with spaces.

        Args:
            text: Text to process.

        Returns:
            Text with special characters replaced by spaces.
        """
        pattern = r"[^a-zA-Z0-9\s]"
        processed_text = re.sub(pattern, " ", text)
        return processed_text

    @staticmethod
    def prepare_keywords(
        metadata_keywords: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
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

    def extract_metadata(self, filename: str) -> dict:
        """
        Extract metadata from a filename.

        Args:
            filename: A string containing the filename to process.

        Returns:
            A dictionary with extracted metadata.
        """
        assert isinstance(filename, str), "filename must be a string"

        metadata = {}
        parsed_filename = urllib.parse.urlparse(filename).path.split("/")
        # Extract metadata based on keywords
        matches = []
        for i, part in reversed(
            list(enumerate(parsed_filename))
        ):  # start searching from the end
            part = part.lower()
            if part in self.keyword_map:
                category, key = self.keyword_map[part]
                matches.append((i, key))  # store both position and keyword
                if category not in metadata:  # only update if category not already set
                    metadata[category] = matches[0][
                        1
                    ]  # select the keyword that appears last

        # Extract dates from the filename
        for part in reversed(parsed_filename):
            if "date" in metadata:
                break
            part = self.replace_special_characters_with_spaces(part)
            for pattern in self.date_patterns:
                match = re.search(pattern, part)
                if match:
                    metadata["date"] = match.group()
                    break

        if not metadata:
            print("No matching metadata found in filename.")

        metadata["filename"] = filename
        return metadata
