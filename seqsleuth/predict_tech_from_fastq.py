import pysam
import logging
from typing import List, Generator

logging.basicConfig(level=logging.INFO)


class FastqRecordReader:
    def __init__(self, filename: str, num_reads: int):
        self.filename = filename
        self.num_reads = num_reads

    def read_records(self) -> Generator[pysam.FastxRecord, None, None]:
        """
        Yield records one by one until chunk size is reached.
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
                    logging.error(f"Error reading file, retrying... ({3 - tries} attempts left)")
                else:
                    logging.error(f"Error reading file, no attempts left. Exception: {e}")
                    raise e


class TechnologyPredictor:
    def __init__(self, reader: FastqRecordReader):
        self.reader = reader

    def is_short_read_technology(self) -> bool:
        """
        Determine if the technology is short read based on max read length.
        """
        max_length = max(len(record.sequence) for record in self.reader.read_records())
        return max_length < 1000

    def predict_technology_based_on_read_names(self) -> str:
        for record in self.reader.read_records():
            read_name = record.name
            if read_name.split(":")[1].isdigit():
                return "Illumina"
            elif read_name.startswith("m") or read_name.startswith("c"):
                return "PacBio"
            elif read_name.startswith("read"):
                return "OxfordNanopore"
        return "Unknown"


class FastqFile:
    def __init__(self, reader: FastqRecordReader, filename: str):
        self.reader = reader
        self.filename = filename
        self.read_names = self._get_read_names()

    def _get_read_names(self) -> List[str]:
        logging.info(f"Getting read names from {self.filename}")
        read_names = []
        for record in self.reader.read_records():
            if record.comment:
                read_name = record.name + " " + record.comment
            else:
                read_name = record.name
            read_names.append(read_name)
        return read_names

    def predict_technology_based_on_filename(self) -> str:
        try:
            ...
        except Exception as e:
            logging.error(f"Error predicting technology based on filename: {e}")
            return "Unknown"


def predict_sequencing_tech(filename: str, num_reads: int = 5) -> str:
    try:
        reader = FastqRecordReader(filename, num_reads)
        fastq_file = FastqFile(reader, filename)
    except IOError as e:
        raise IOError(f"Error initializing FastqFile: {e}")

    try:
        tech_from_filepath = fastq_file.predict_technology_based_on_filename()
        logging.info(f"tech from filepath: {tech_from_filepath}")
    except Exception as e:
        return f"Error predicting technology based on filename: {e}"

    return tech_from_filepath
import pysam
import logging
from typing import List, Generator

logging.basicConfig(level=logging.INFO)


class FastqRecordReader:
    def __init__(self, filename: str, num_reads: int):
        self.filename = filename
        self.num_reads = num_reads

    def read_records(self) -> Generator[pysam.FastxRecord, None, None]:
        """
        Yield records one by one until chunk size is reached.
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
                    logging.error(f"Error reading file, retrying... ({3 - tries} attempts left)")
                else:
                    logging.error(f"Error reading file, no attempts left. Exception: {e}")
                    raise e


class TechnologyPredictor:
    def __init__(self, reader: FastqRecordReader):
        self.reader = reader

    def is_short_read_technology(self) -> bool:
        """
        Determine if the technology is short read based on max read length.
        """
        max_length = max(len(record.sequence) for record in self.reader.read_records())
        return max_length < 1000

    def predict_technology_based_on_read_names(self) -> str:
        for record in self.reader.read_records():
            read_name = record.name
            if read_name.split(":")[1].isdigit():
                return "Illumina"
            elif read_name.startswith("m") or read_name.startswith("c"):
                return "PacBio"
            elif read_name.startswith("read"):
                return "OxfordNanopore"
        return "Unknown"


class FastqFile:
    def __init__(self, reader: FastqRecordReader, filename: str):
        self.reader = reader
        self.filename = filename
        self.read_names = self._get_read_names()

    def _get_read_names(self) -> List[str]:
        logging.info(f"Getting read names from {self.filename}")
        read_names = []
        for record in self.reader.read_records():
            if record.comment:
                read_name = record.name + " " + record.comment
            else:
                read_name = record.name
            read_names.append(read_name)
        return read_names

    def predict_technology_based_on_filename(self) -> str:
        try:
            ...
        except Exception as e:
            logging.error(f"Error predicting technology based on filename: {e}")
            return "Unknown"


def predict_sequencing_tech(filename: str, num_reads: int = 5) -> str:
    try:
        reader = FastqRecordReader(filename, num_reads)
        fastq_file = FastqFile(reader, filename)
    except IOError as e:
        raise IOError(f"Error initializing FastqFile: {e}")

    try:
        tech_from_filepath = fastq_file.predict_technology_based_on_filename()
        logging.info(f"tech from filepath: {tech_from_filepath}")
    except Exception as e:
        return f"Error predicting technology based on filename: {e}"

    return tech_from_filepath
