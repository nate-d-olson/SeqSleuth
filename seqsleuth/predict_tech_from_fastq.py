import pysam

class FastqRecordReader:
    def __init__(self, filename, chunk_size):
        self.filename = filename
        self.chunk_size = chunk_size

def read_records(self):
    """Yield records one by one until chunk size is reached"""
    size = 0
    tries = 3
    while tries > 0:
        try:
            with pysam.FastxFile(self.filename, "fastq") as fh:
                for record in fh:
                    yield record
                    size += len(record.sequence)
                    if size >= self.chunk_size:
                        break
            break  # If the file read is successful, break the retry loop.
        except Exception as e:
            tries -= 1
            if tries > 0:
                print(f"Error reading file, retrying... ({3 - tries} attempts left)")
            else:
                print(f"Error reading file, no attempts left. Exception: {e}")
                raise e

class TechnologyPredictor:
    def __init__(self, reader):
        self.reader = reader

    def is_short_read_technology(self):
        """Determine if the technology is short read based on max read length"""
        max_length = max(len(record.sequence) for record in self.reader.read_records())
        return max_length < 1000

    def predict_technology_based_on_read_names(self):
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
    def __init__(self, reader, filename):
        self.reader = reader
        self.filename = filename
        self.read_names = self._get_read_names()
    
    def _get_read_names(self):
        print("Getting read names from " + self.filename)
        read_names = []
        for record in self.reader.read_records():
            if record.comment:
                read_name = record.name + " " + record.comment
            else:
                read_name = record.name
            read_names.append(read_name)
        return read_names

    def predict_technology_based_on_filename(self):
        try:
            filename_lower = self.filename.lower()
            if any(substring in filename_lower for substring in ["illumina", "ilum", "nextseq", "hiseq", "miseq", "novaseq", "ill"]):
                return "Illumina"
            elif any(substring in filename_lower for substring in ["pacbio", "pb", "sequel", "smrt"]):
                return "PacBio"
            elif any(substring in filename_lower for substring in ["nanopore", "ont", "minion", "promethion"]):
                return "OxfordNanopore"
            elif any(substring in filename_lower for substring in ["bgi"]):
                return "BGI"
            elif any(substring in filename_lower for substring in ["completegenomics"]):
                return "CompleteGenomics"
            elif any(substring in filename_lower for substring in ["dovetail"]):
                return "Dovetail"
            elif any(substring in filename_lower for substring in ["strandseq"]):
                return "StrandSeq"
            elif any(substring in filename_lower for substring in ["10xgenomics"]):
                return "10XGenomics"
            elif any(substring in filename_lower for substring in ["moleculo"]):
                return "Moleculo"
            else:
                return "Unknown"
        except Exception as e:
            print(f"Error predicting technology based on filename: {e}")
            return "Unknown"

def predict_sequencing_tech(filename, chunk_size=1e9):
    try:
        reader = FastqRecordReader(filename, chunk_size)
        fastq_file = FastqFile(reader, filename)
        # tech_predictor = TechnologyPredictor(reader)
    except IOError as e:
        raise IOError(f"Error initializing FastqFile: {e}")

    # try:
    #     short_read = tech_predictor.is_short_read_technology()
    # except ValueError as e:
    #     raise ValueError(f"Error determining if short read technology: {e}")

    try:
        tech_from_filepath = fastq_file.predict_technology_based_on_filename()
        print(f"tech from filepath: {tech_from_filepath}")
    except Exception as e:
        return f"Error predicting technology based on filename: {e}"

    # if tech_from_filepath != "Unknown":
    #     if (short_read and tech_from_filepath == "Illumina") or (
    #         not short_read and tech_from_filepath in ["PacBio", "OxfordNanopore"]
    #     ):
    #         return tech_from_filepath
    #     else:
    #         return f"Inconsistent read length and technology detected in filepath: {tech_from_filepath}"

    # try:
    #     tech_from_read_names = tech_predictor.predict_technology_based_on_read_names()
    # except Exception as e:
    #     return f"Error predicting technology based on read names: {e}"

    # if tech_from_read_names != "Unknown":
    #     return tech_from_read_names

    return tech_from_filepath
