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
        self.metadata = {}

    def check_read_name_convention(self, read_name: str):
        pass

    def extract_metadata_from_read(self, read_name: str):
        pass

    def get_metadata_fields(self):
        pass

class OxfordNanopore(SeqTech):
    def __init__(self, fastq_file: FastqFile):
        super().__init__(fastq_file)
        self.earliest_start_date = None

    def check_read_name_convention(self, read_name):
        pattern = re.compile(
            "^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12} runid=[0-9a-f]{40}.*$"
        )

        match = pattern.match(read_name) is not None
        if match:
            logger.error(
                f"Error: Read name '{read_name}' does not match Oxford Nanopore pattern. Read name: {read_name}, Metadata: {self.metadata}"
            )
        return match

    def extract_metadata_from_read(self, read_name):
        try:
            if not self.check_read_name_convention(read_name):
                raise ValueError(
                    "Read name convention check failed for read id: " + read_name
                )

            # Extracting metadata from Oxford Nanopore read names:
            metadata = {}
            parts = read_name.split()

            # The first field is the runid
            metadata["runid"] = parts[1].split("=")[1]

            # Parse additional key-value pairs
            for pair in parts[1:]:
                key, value = pair.split("=")
                if key not in ["read", "ch"]:
                    if key in metadata:
                        if value not in metadata[key]:
                            metadata[key].append(value)
                    else:
                        metadata[key] = [value]

            # Parse the start_time and update earliest_start_date if this date is earlier
            start_time = datetime.strptime(
                metadata.get("start_time", ""), "%Y-%m-%dT%H:%M:%SZ"
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

            # Remove the start_time field
            metadata.pop("start_time", None)

            return metadata

        except ValueError as error:
            print(error)
            return {}

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata.keys())
        return metadata_fields


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

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata.keys())
        return metadata_fields


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

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata.keys())
        return metadata_fields


class TenXGenomicsLinkedReads(SeqTech):
    def __init__(self, fastq_file):
        super().__init__(fastq_file)
        self.metadata_values = []

    def check_read_name_convention(self, read_name):
        pattern = re.compile(r"^\S+:\S+:\S+:\S+:\S+:.*$")

        match = pattern.match(read_name) is not None
        if not match:
            logger.error(f"Error: Read name '{read_name}' does not match 10X Genomics Linked-Reads pattern.")
        return match

    def extract_metadata_from_read(self, read_name):
        if not self.check_read_name_convention(read_name):
            logger.error("Read name convention check failed for read id: " + read_name)
            return {}

        # Extracting metadata from 10X Genomics Linked-Reads read names:
        metadata = {}
        parts = read_name.split(":")

        # The first field is the sample identifier
        metadata["sample"] = parts[0]

        # The second field is the library identifier
        metadata["library"] = parts[1]

        # The fourth field is the set identifier
        metadata["set"] = parts[3]

        # Append the metadata values to the list
        self.metadata_values.append(metadata)

        return metadata

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata_values[0].keys()) if self.metadata_values else []
        return metadata_fields

    def get_unique_metadata_values(self):
        unique_values = []
        for metadata in self.metadata_values:
            for value in metadata.values():
                if value not in unique_values:
                    unique_values.append(value)
        return unique_values


class DovetailSeqTech(SeqTech):
    def __init__(self, fastq_file):
        super().__init__(fastq_file)
        self.n_reads = 0

    def check_read_name_convention(self, read_name):
        pattern = re.compile(r"^(\S+:\S+:\S+:\S+:\S+:\S+:\S+)\s(\d:\S:\d:\S+)$")

        match = pattern.match(read_name) is not None
        if not match:
            logger.error(
                f"Error: Read name '{read_name}' does not match Dovetail Genomics pattern. Read name: {read_name}, Metadata: {self.metadata}"
            )
        return match

    def extract_metadata_from_read(self, read_name):
        self.n_reads += 1

        if not self.check_read_name_convention(read_name):
            logger.error(
                f"Read name convention check failed for read id: {read_name}, Metadata: {self.metadata}"
            )
            return {}

        # Extracting metadata from Dovetail Genomics read names:
        parts = read_name.split(" ")

        # Assuming the first field contains the library identifier and other fields
        library_info = parts[0].split(":")

        # Assuming the second field contains the read number and other fields
        ## Not extracting read fields as they are unique for each read
        # read_info = parts[1].split(":")

        # Extracting library and instrument info
        for i, field in enumerate(library_info[:5]):
            ## 6th field is read number and unique per read
            field_name = f"Library_Field_{i + 1}"
            if field_name in self.metadata:
                if field not in self.metadata[field_name]:
                    self.metadata[field_name].append(field)
            else:
                self.metadata[field_name] = [field]
                    
        

        return self.metadata

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata.keys())
        return metadata_fields


class SeqTechFactory:
    @staticmethod
    def get_tech_class(tech_name, fastq_file):
        if tech_name == "Illumina":
            return Illumina(fastq_file)
        elif tech_name == "PacBio":
            return PacBio(fastq_file)
        elif tech_name == "OxfordNanopore":
            return OxfordNanopore(fastq_file)
        elif tech_name == "10XGenomics":
            return TenXGenomicsLinkedReads(fastq_file)
        elif tech_name == "Dovetail":
            return DovetailSeqTech(fastq_file)
        else:
            raise ValueError(f"No method implemented to extract metadata from {tech_name}")
