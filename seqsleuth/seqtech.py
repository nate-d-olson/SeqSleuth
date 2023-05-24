import re
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Type
from datetime import datetime


@dataclass
class SeqTech:
    read_names: List[str]
    logger: Any = field(init=False, repr=False)

    def __post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_read_name_convention(self, read_name: str) -> bool:
        raise NotImplementedError()

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, str]:
        raise NotImplementedError()

    def get_metadata_fields(self) -> List[str]:
        raise NotImplementedError()


@dataclass
class Illumina(SeqTech):
    read_names: List[str]
    illumina_pattern: re.Pattern = re.compile(
        "^[\w-]+:\d+:[\w-]+:\d+:\d+:\d+:\d+\s[12]:[YN]:\d+:[ATCGN+]+$"
    )

    def check_read_name_convention(self, read_name: str) -> bool:
        match = self.illumina_pattern.match(read_name) is not None
        if not match:
            self.logger.error(
                f"Error: Read name '{read_name}' does not match Illumina pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, str]:
        if not self.check_read_name_convention(read_name):
            self.logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        metadata = {}
        parts = read_name.split(":")

        metadata["instrument_id"] = parts[0]
        metadata["run_number"] = int(parts[1])
        metadata["flow_cell_id"] = parts[2]
        metadata["flow_cell_lane"] = int(parts[3])

        return metadata

    def get_metadata_fields(self) -> List[str]:
        return ["instrument_id", "run_number", "flow_cell_id", "flow_cell_lane"]


@dataclass
class PacBio(SeqTech):
    read_names: List[str]
    pacbio_pattern_clr: re.Pattern = re.compile(
        "^m\d+_\d+_\d+_c\d+_s\d+_p\d+/\d+/\d+_\d+$"
    )
    pacbio_pattern_ccs: re.Pattern = re.compile("^m\d+_\d+_\d+\d+/\d+/ccs")

    def check_read_name_convention(self, read_name: str) -> bool:
        match = (
            self.pacbio_pattern_clr.match(read_name) is not None
            or self.pacbio_pattern_ccs.match(read_name) is not None
        )
        if not match:
            self.logger.error(
                f"Error: Read name '{read_name}' does not match PacBio pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name):
        if not self.check_read_name_convention(read_name):
            self.logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        # Extracting metadata from PacBio read names:
        metadata = {}
        parts = read_name.split("/")

        # The first field contains the movie name
        metadata["movie_name"] = parts[0].split("_")[0]

        # Check if it's a CCS read
        if parts[2] == "ccs":
            metadata["read_type"] = "CCS"
        else:
            metadata["read_type"] = "CLR"

        return metadata

    def get_metadata_fields(self):
        metadata_fields = list(self.metadata.keys())
        return metadata_fields


@dataclass
class OxfordNanopore(SeqTech):
    read_names: List[str]
    nanopore_pattern: re.Pattern = re.compile(
        r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12} runid=[0-9a-f]{40}.*$"
    )
    earliest_start_date: Optional[datetime] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def check_read_name_convention(self, read_name: str) -> bool:
        match = self.nanopore_pattern.match(read_name) is not None
        if not match:
            self.logger.error(
                f"Error: Read name '{read_name}' does not match Oxford Nanopore pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, str]:
        if not self.check_read_name_convention(read_name):
            self.logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        parts = read_name.split()
        for pair in parts[1:]:
            key, value = pair.split("=")
            if key not in ["read", "ch"]:
                self.metadata[key] = value

        start_time = datetime.strptime(
            self.metadata.get("start_time", ""), "%Y-%m-%dT%H:%M:%SZ"
        ).date()
        if self.earliest_start_date is None or start_time < self.earliest_start_date:
            self.earliest_start_date = start_time

        self.metadata["earliest_start_date"] = self.earliest_start_date.strftime(
            "%Y-%m-%d"
        )
        self.metadata.pop("start_time", None)

        return self.metadata

    def get_metadata_fields(self) -> List[str]:
        return list(self.metadata.keys())


@dataclass
class TenXGenomicsLinkedReads(SeqTech):
    read_names: List[str]
    linkedreads_pattern: re.Pattern = re.compile(r"^\S+:\S+:\S+:\S+:\S+:.*$")
    metadata_values: List[Dict[str, str]] = field(default_factory=list)

    def check_read_name_convention(self, read_name: str) -> bool:
        match = self.linkedreads_pattern.match(read_name) is not None
        if not match:
            self.logger.error(
                f"Error: Read name '{read_name}' does not match 10X Genomics Linked-Reads pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, str]:
        if not self.check_read_name_convention(read_name):
            self.logger.error(
                "Read name convention check failed for read id: " + read_name
            )
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

    def get_metadata_fields(self) -> List[str]:
        return ["sample", "library", "set"]


@dataclass
class DovetailSeqTech(SeqTech):
    read_names: List[str]
    dovetail_pattern: re.Pattern = re.compile(
        r"^(\S+:\S+:\S+:\S+:\S+:\S+:\S+)\s(\d:\S:\d:\S+)$"
    )
    metadata: Dict[str, List[str]] = field(default_factory=dict)
    n_reads: int = 0

    def check_read_name_convention(self, read_name: str) -> bool:
        match = self.dovetail_pattern.match(read_name) is not None
        if not match:
            self.logger.error(
                f"Error: Read name '{read_name}' does not match Dovetail Genomics pattern."
            )
        return match

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, List[str]]:
        if not self.check_read_name_convention(read_name):
            self.logger.error(
                "Read name convention check failed for read id: " + read_name
            )
            return {}

        # Extracting metadata from Dovetail Genomics read names:
        parts = read_name.split(" ")

        # Assuming the first field contains the library identifier and other fields
        library_info = parts[0].split(":")

        # Extracting library and instrument info
        for i, field in enumerate(library_info[:5]):
            ## 6th field is read number and unique per read
            field_name = f"Library_Field_{i + 1}"
            self.metadata[field_name] = field

        return self.metadata

    def get_metadata_fields(self) -> List[str]:
        return list(self.metadata.keys())


@dataclass
class OtherSeqTech(SeqTech):
    def check_read_name_convention(self, read_name: str) -> bool:
        # As the convention for "Other" is not defined, you may return True or apply some conditions as needed
        return True

    def extract_metadata_from_read(self, read_name: str) -> Dict[str, Any]:
        # Returns the desired dictionary format as metadata
        return {"tech": "unimplemented parser", "read_names": read_name}

    def get_metadata_fields(self) -> List[str]:
        # If required, you can list the fields that this class will return in metadata
        return ["tech", "read_names"]


@dataclass
class UnknownSeqTech(SeqTech):
    read_names: List[str]
    tech: str = "Unknown"
    read_name_regex: str = r".*"
    read_name_pattern: Any = field(init=False, repr=False)

    def __post_init__(self):
        self.read_name_pattern = re.compile(self.read_name_regex)

    def format_reads(self):
        return {"tech": self.tech, "read_names": self.read_names}


class SeqTechFactory:
    def __init__(
        self, predicted_tech: str, read_names: List[str], logging_level: str = "INFO"
    ):
        self.predicted_tech = predicted_tech
        self.read_names = read_names
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)

        self.seqtech_classes: Dict[str, Type[SeqTech]] = {
            "Illumina": Illumina,
            "OxfordNanopore": OxfordNanopore,
            "PacBio": PacBio,
            "10XGenomics": TenXGenomicsLinkedReads,
            "Dovetail": DovetailSeqTech,
            "Unknown": UnknownSeqTech,
            "Other": OtherSeqTech,
        }

    def create(self) -> SeqTech:
        seqtech_class = self.seqtech_classes.get(self.predicted_tech, OtherSeqTech)
        try:
            instance = seqtech_class(self.read_names)
            return instance
        except Exception as e:
            self.logger.error(
                f"An error occurred while attempting to create an instance of {seqtech_class.__name__}: {str(e)}"
            )
            return UnknownSeqTech(self.read_names)

    def extract_metadata_in_parallel(self, seqtech_instance, n_workers):
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            metadata_list = list(
                executor.map(
                    seqtech_instance.extract_metadata_from_read, self.read_names
                )
            )

        return metadata_list
