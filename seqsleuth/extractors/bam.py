import logging
import pysam
import os


import os


class BAMFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.filetype = "bam"
        self.extractor = BAMMetadataExtractor(filepath)

    def metadata(self):
        """Extract metadata from the BAM file."""
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "filetype": self.filetype,
            "metadata": self.extractor.extract_metadata(),
        }


class BAMMetadataExtractor:
    def __init__(self, filepath):
        self.filepath = filepath

    def extract_metadata(self):
        metadata = {}

        try:
            bamfile = pysam.AlignmentFile(self.filepath, "rb")

            # Get the header as a dictionary
            metadata["header"] = bamfile.header.to_dict()

            # Get the name of the first read
            first_read_name = next(bamfile).query_name

            bamfile.close()

            # Add the first read name and url to the header dictionary
            metadata["first_read_name"] = first_read_name
            metadata["url"] = self.filepath

            return metadata

        except Exception as e:
            logging.error(
                f"Failed to process BAM file at {self.filepath}. Error: {str(e)}"
            )
            return {"url": self.filepath, "error": str(e)}
