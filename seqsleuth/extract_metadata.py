# metadata_extractor.py
import logging
from predict_tech_from_fastq import FastqFile
from seqtech import SeqTechFactory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataExtractor:
    def __init__(self, fastq_file: FastqFile, filename: str, predicted_tech: str):
        self.fastq_file = fastq_file
        self.filename = filename
        self.predicted_tech = predicted_tech
        self.tech_class = self._get_tech_class()
        self.metadata = {}

    def _get_tech_class(self):
        try:
            return SeqTechFactory.get_tech_class(self.predicted_tech, self.fastq_file)
        except ValueError as e:
            logger.error(e)
            return None

    def extract_metadata(self):
        if self.tech_class is None:
            logger.error("No tech class available for metadata extraction.")
            return {}

        for read_name in self.fastq_file.read_names:
            try:
                if not self.tech_class.check_read_name_convention(read_name):
                    logger.error(
                        f"Read names do not match expected convention for {self.predicted_tech}"
                    )
                    continue
                metadata = self.tech_class.extract_metadata_from_read(read_name)
                if not metadata:
                    logger.error(f"Failed to extract metadata from read: {read_name}")
                    continue
                self.metadata.update(metadata)  # Update overall metadata with new data
            except Exception as e:
                logger.error(f"Exception occurred during metadata extraction: {e}")
        return self.metadata
