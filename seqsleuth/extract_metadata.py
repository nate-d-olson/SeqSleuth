import logging
from predict_tech_from_fastq import FastqFile
from seqtech import SeqTechFactory
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataExtractor:
    def __init__(self, fastq_file: FastqFile, filename: str, predicted_tech: str):
        self.filename = filename
        self.predicted_tech = predicted_tech
        self.tech_instance = self._get_tech_instance(fastq_file.read_names)

    def _get_tech_instance(self, read_names: List[str]):
        factory = SeqTechFactory(self.predicted_tech, read_names)
        return factory.create()

    def extract_metadata(self):
        try:
            if self.tech_instance is None:
                logger.error("No tech class available for metadata extraction.")
                return {}

            metadata_dict = {}
            for read_name in self.tech_instance.read_names:
                read_metadata = self.tech_instance.extract_metadata_from_read(read_name)
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
