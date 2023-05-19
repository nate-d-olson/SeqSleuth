# seqtech.py
import re
from datetime import datetime
from predict_tech_from_fastq import FastqFile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeqTech:
    def __init__(self, fastq_file: FastqFile):
        self.fastq_file = fastq_file

    def check_read_name_convention(self, read_name: str):
        pass

    def extract_metadata_from_read(self, read_name: str):
        pass


class OxfordNanopore(SeqTech):
    def __init__(self, fastq_file: FastqFile):
        super().__init__(fastq_file)
        self.earliest_start_date = None

    def check_read_name_convention(self, read_name):
        pattern = re.compile(
            "^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12} runid=[0-9a-f]{40} read=\d+ ch=\d+ start_time=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        )

        match = pattern.match(read_name) is not None
        if not match:
            logger.error(
                f"Error: Read name '{read_name}' does not match Oxford Nanopore pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name):
        if not self.check_read_name_convention(read_name):
            logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        # Extracting metadata from Oxford Nanopore read names:
        metadata = {}
        parts = read_name.split()

        # The first field is the runid
        metadata["runid"] = parts[1].split("=")[1]

        # Parse the start_time and update earliest_start_date if this date is earlier
        start_time = datetime.strptime(
            parts[4].split("=")[1], "%Y-%m-%dT%H:%M:%SZ"
        ).date()
        if (
            self.earliest_start_date is None
            or start_time < self.earliest_start_date
        ):
            self.earliest_start_date = start_time

        # Add the earliest_start_date to the metadata
        metadata["earliest_start_date"] = self.earliest_start_date.strftime(
            "%Y-%m-%d"
        )

        return metadata


class PacBio(SeqTech):
    def __init__(self, fastq_file: FastqFile):
        super().__init__(fastq_file)

    def check_read_name_convention(self, read_name):
        pattern_clr = re.compile("^m\d+_\d+_\d+_c\d+_s\d+_p\d+/\d+/\d+_\d+$")
        pattern_ccs = re.compile("^m\d+_\d+_\d+\d+/\d+/ccs$")

        match = (
            pattern_clr.match(read_name) is not None
            or pattern_ccs.match(read_name) is not None
        )
        if not match:
            logger.error(f"Error: Read name '{read_name}' does not match PacBio pattern.")
        return match

    def extract_metadata_from_read(self, read_name):
        if not self.check_read_name_convention(read_name):
            logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        # Extracting metadata from PacBio read names:
        metadata = {}
        parts = read_name.split("/")

        # The first field contains the movie name
        metadata["movie_name"] = parts[0]

        # Check if it's a CCS read
        if parts[2] == "ccs":
            metadata["read_type"] = "CCS"
        else:
            metadata["read_type"] = "CLR"

        return metadata


class Illumina(SeqTech):
    def __init__(self, fastq_file: FastqFile):
        super().__init__(fastq_file)

    def check_read_name_convention(self, read_name):
        pattern = re.compile(
            "^[\w-]+:\d+:[\w-]+:\d+:\d+:\d+:\d+\s[12]:[YN]:\d+:[ATCGN+]+$"
        )

        match = pattern.match(read_name) is not None
        if not match:
            logger.error(f"Error: Read name '{read_name}' does not match Illumina pattern.")
        return match

    def extract_metadata_from_read(self, read_name):
        if not self.check_read_name_convention(read_name):
            logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        # Extracting metadata from Illumina read names:
        metadata = {}
        parts = read_name.split(":")

        # The first field contains the instrument id
        metadata["instrument_id"] = parts[0]

        # The second field is the run number
        metadata["run_number"] = int(parts[1])

        # The third field is the flow cell id
        metadata["flow_cell_id"] = parts[2]

        # The fourth field is the flow cell lane
        metadata["flow_cell_lane"] = int(parts[3])

        return metadata


class SeqTechFactory:
    @staticmethod
    def get_tech_class(tech_name: str, fastq_file: FastqFile):
        if tech_name == "Illumina":
            return Illumina(fastq_file)
        elif tech_name == "PacBio":
            return PacBio(fastq_file)
        elif tech_name == "OxfordNanopore":
            return OxfordNanopore(fastq_file)
        else:
            raise ValueError(f"Unrecognized technology: {tech_name}")
