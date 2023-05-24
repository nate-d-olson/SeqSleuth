import pysam
import logging
from typing import List, Generator

logging.basicConfig(level=logging.INFO)

# Define constants for technology names
TECH_ILLUMINA = "Illumina"
TECH_PACBIO = "PacBio"
TECH_OXFORDNANOPORE = "OxfordNanopore"
TECH_BGI = "BGI"
TECH_COMPLETEGENOMICS = "CompleteGenomics"
TECH_DOVETAIL = "Dovetail"
TECH_STRANDSEQ = "StrandSeq"
TECH_10XGENOMICS = "10XGenomics"
TECH_MOLECULO = "Moleculo"
TECH_UNKNOWN = "Unknown"
TECH_ASSEMBLY = "Assembly"
TECH_ION = "IonTorrent"

# Define constants for technology filename identifiers
TECH_IDENTIFIERS = {
    TECH_ASSEMBLY: ["asm","assembly","assemblies"],
    TECH_ILLUMINA: ["illumina", "ilum", "nextseq", "hiseq", "miseq", "novaseq", "ill"],
    TECH_PACBIO: ["pacbio", "pb", "sequel", "smrt"],
    TECH_OXFORDNANOPORE: ["nanopore", "ont", "minion", "promethion"],
    TECH_BGI: ["bgi"],
    TECH_COMPLETEGENOMICS: ["completegenomics"],
    TECH_DOVETAIL: ["dovetail"],
    TECH_STRANDSEQ: ["strandseq", "strand-seq"],
    TECH_10XGENOMICS: ["10xgenomics"],
    TECH_MOLECULO: ["moleculo"],
    TECH_ION: ["ion_exome","torrent"]
}

# Define the max length for short read
MAX_LENGTH_SHORT_READ = 1000


class FastqRecordReader:
    def __init__(self, filename: str, num_reads: int):
        self.filename = filename
        self.num_reads = num_reads

    def read_records(self) -> Generator[pysam.FastxRecord, None, None]:
        """
        Yield records one by one until num reads is reached.
        """
        tries = 3
        while tries > 0:
            count = 0
            try:
                with pysam.FastxFile(self.filename, "fastq") as fh:
                    for record in fh:
                        yield record
                        count += 1
                        if self.num_reads != -1 and count >= self.num_reads:
                            break
                break
            except Exception as e:
                tries -= 1
                if tries > 0:
                    logging.error(
                        f"Error reading file, retrying... ({3 - tries} attempts left)"
                    )
                else:
                    logging.error(
                        f"Error reading file, no attempts left. Exception: {e}"
                    )
                    raise e


class TechnologyPredictor:
    def __init__(self):
        pass

    def is_short_read_technology(self) -> bool:
        """
        Determine if the technology is short read based on max read length.
        """
        max_length = max(len(record.sequence) for record in self.records)
        return max_length < 1000

    def predict_technology_based_on_read_names(self) -> str:
        for record in self.records:
            read_name = record.name
            if read_name.split(":")[1].isdigit():
                return "Illumina"
            elif read_name.startswith("m") or read_name.startswith("c"):
                return "PacBio"
            elif read_name.startswith("read"):
                return "OxfordNanopore"
        return "Unknown"


class FastqFile:
    def __init__(self, records: List[pysam.FastxRecord], filename: str):
        self.records = records
        self.filename = filename
        self.read_names = self._get_read_names()

    def _get_read_names(self) -> List[str]:
        logging.debug(f"Getting read names from {self.filename}")
        read_names = []
        for record in self.records:
            if record.comment:
                read_name = record.name + " " + record.comment
            else:
                read_name = record.name
            read_names.append(read_name)
        return read_names

    def predict_technology_based_on_filename(self) -> str:
        try:
            filename_lower = self.filename.lower()
            for tech, identifiers in TECH_IDENTIFIERS.items():
                if any(substring in filename_lower for substring in identifiers):
                    return tech
            return TECH_UNKNOWN
        except Exception as e:
            logging.error(f"Error predicting technology based on filename: {e}")
            return TECH_UNKNOWN


def predict_sequencing_tech(filename: str, num_reads: int = 5) -> str:
    try:
        reader = FastqRecordReader(filename, num_reads)
        records = list(reader.read_records())
        fastq_file = FastqFile(records, filename)
    except IOError as e:
        raise IOError(f"Error initializing FastqFile: {e}")

    try:
        tech_from_filepath = fastq_file.predict_technology_based_on_filename()
        logging.debug(
            f"Predicted tech from filepath: {tech_from_filepath}, for {filename}"
        )
    except Exception as e:
        return f"Error predicting technology based on filename: {e}"

    return tech_from_filepath
