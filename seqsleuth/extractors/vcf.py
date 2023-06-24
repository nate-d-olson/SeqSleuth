import pysam
import logging
import os


class VCFMetadataExtractor:
    def __init__(self, filepath):
        self.filepath = filepath

    def extract_metadata(self):
        try:
            with pysam.VariantFile(self.filepath) as vcffile:
                header_fileformat = vcffile.header.version
                header_samples = list(vcffile.header.samples)

                header_dict = {
                    "fileformat": header_fileformat,
                    "samples": header_samples,
                }

                # Initialize optional fields with None
                date, source, reference = None, None, None

                # Iterate over the header lines
                for record in vcffile.header.records:
                    if record.key not in ["contig", "INFO", "FORMAT", "FILTER"]:
                        header_dict[record.key] = record.value

                return {"url": self.filepath, "header": header_dict}
        except Exception as e:
            logging.error(
                f"Failed to process VCF file at {self.filepath}. Error: {str(e)}"
            )
            return {"url": self.filepath, "header": None, "error": str(e)}


class VCFFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.filetype = "vcf"
        self.extractor = VCFMetadataExtractor(filepath)

    def metadata(self):
        """Extract metadata from the VCF file."""
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "filetype": self.filetype,
            "metadata": self.extractor.extract_metadata(),
        }
