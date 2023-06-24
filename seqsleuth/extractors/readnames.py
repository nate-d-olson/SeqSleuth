import logging
from typing import List

from seqsleuth.predict_tech_from_fastq import FastqFile
from extractors.seqtech import SeqTechFactory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReadNameMetadataExtractor:
    def __init__(self, fastq_file: FastqFile, filename: str, predicted_tech: str):
        self.filename = filename
        self.predicted_tech = predicted_tech
        self.read_names = fastq_file.read_names
        self.factory = SeqTechFactory(self.predicted_tech, self.read_names)
        self.tech_instance = self.factory.create()

    def extract_metadata(self):
        try:
            if self.tech_instance is None:
                logger.error("No tech class available for metadata extraction.")
                return {}

            metadata_dict = {}

            # Extract metadata from all read names sequentially
            metadata_list = self.extract_metadata_sequentially()

            for read_metadata in metadata_list:
                if read_metadata:  # only process non-empty metadata
                    for key, value in read_metadata.items():
                        if key not in metadata_dict:
                            metadata_dict[key] = set()  # create a new set for this key
                        metadata_dict[key].add(value)  # add the new value to the set

            # Convert sets to single values or lists, as appropriate
            for key, value_set in metadata_dict.items():
                if len(value_set) == 1:
                    metadata_dict[key] = next(iter(value_set))  # single value
                else:
                    metadata_dict[key] = list(value_set)  # list of unique values

            return metadata_dict

        except Exception as e:
            logger.error(f"Exception occurred during metadata extraction: {e}")
            return {}

    def extract_metadata_sequentially(self):
        metadata_list = []
        for read_name in self.read_names:
            metadata_list.append(
                self.tech_instance.extract_metadata_from_read(read_name)
            )

        return metadata_list
