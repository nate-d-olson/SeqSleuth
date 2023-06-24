import argparse
import concurrent.futures
import csv
import json
import logging
import os
import sys
from multiprocessing import cpu_count
from typing import Any, Dict, List
from urllib.parse import urlparse

from extractors.readnames import ReadNameMetadataExtractor
from predict_tech_from_fastq import (
    FastqFile,
    FastqRecordReader,
    predict_sequencing_tech,
)
from tqdm import tqdm
from parser_filename import FilenameMetadataExtractor
from extractors.bam import BAMMetadataExtractor, BAMFile
from extractors.vcf import VCFMetadataExtractor, VCFFile
from keywords.fastq import metadata_keywords as fastq_keys
from keywords.bam import metadata_keywords as bam_keys
from keywords.vcf import metadata_keywords as vcf_keys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def process_file(file_type: str, filename: str, num_reads: int) -> Dict[str, Any]:
    logging.debug(f"Processing file: {filename} in process id: {os.getpid()}")
    try:
        if file_type == "fastq":
            reader = FastqRecordReader(filename, num_reads)
            records = list(reader.read_records())
            file = FastqFile(records, filename)
            predicted_tech = predict_sequencing_tech(filename)
            extractor = ReadNameMetadataExtractor(file, filename, predicted_tech)
            metadata = extractor.extract_metadata()
            metadata_keywords = fastq_keys
        elif file_type == "bam":
            file = BAMFile(filename)
            metadata = file.metadata()
            metadata_keywords = bam_keys
        elif file_type == "vcf":
            file = VCFFile(filename)
            metadata = file.metadata()
            metadata_keywords = vcf_keys

        filename_extractor = FilenameMetadataExtractor(metadata_keywords)
        filename_metadata = filename_extractor.extract_metadata(filename)
        metadata.update(filename_metadata)

        return {"filename": filename, "metadata": json.dumps(metadata)}

    except Exception as e:
        logging.error(
            f"Error processing file in `process_file`: {filename}. Error message: {str(e)}"
        )


def main(
    file_info: List[Dict[str, str]],
    output_dir: str,
    num_reads: int,
    num_workers: int,
    show_progress: bool,
) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Warning: The directory {output_dir} did not exist and was created.")

    for file_type in ["fastq", "bam", "vcf"]:
        file_info_of_type = [
            info for info in file_info if info["filetype"].lower() == file_type
        ]
        if file_info_of_type:
            with open(
                os.path.join(output_dir, f"{file_type}_metadata.csv"), "w", newline=""
            ) as csvfile:
                fieldnames = ["filename", "metadata"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                pbar = tqdm(total=len(file_info_of_type), disable=not show_progress)

                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=num_workers
                ) as executor:
                    futures = [
                        executor.submit(
                            process_file,
                            file_type,
                            (
                                f"https://ftp-trace.ncbi.nlm.nih.gov"
                                f"/ReferenceSamples/giab/"
                                f"{info['filepath'].replace('/giab/ftp/', '')}/"
                                f"{info['filename']}"
                            ),
                            num_reads,
                        )
                        for info in file_info_of_type
                    ]

                    for future in concurrent.futures.as_completed(futures):
                        writer.writerow(future.result())
                        pbar.update(1)
                pbar.close()


def validate_num_reads(value: str) -> int:
    ivalue = int(value)
    if ivalue <= -2 or ivalue == 0:
        raise argparse.ArgumentTypeError(
            "Please provide a number greater than or equal to -1, where -1 indicates all reads."
        )
    return ivalue


def validate_workers(value: str) -> int:
    if value.lower() == "all":
        return cpu_count()
    else:
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError(
                "Number of workers must be greater than 0."
            )
        return ivalue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Predict the technology and extract metadata from fastq, bam, and vcf files."
    )
    parser.add_argument(
        "file_list",
        type=argparse.FileType("r"),
        help="A file containing a list of fastq files, one per line.",
    )
    parser.add_argument(
        "--num_reads",
        type=validate_num_reads,
        default=5,
        help="Number of reads to process. Defaults to 5. Set to -1 to process all reads.",
    )
    parser.add_argument(
        "--workers",
        type=validate_workers,
        default=1,
        help="Number of worker threads. Defaults to 1. Set to 'all' to use all CPU cores.",
    )
    parser.add_argument("--output_dir", type=str, default=".", help="Output directory.")
    parser.add_argument(
        "--verbose", action="store_true", help="Print detailed messages."
    )
    parser.add_argument("--progress", action="store_true", help="Show progress bar.")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    file_info = []
    reader = csv.DictReader(args.file_list)
    for row in reader:
        file_info.append(row)

    main(file_info, args.output_dir, args.num_reads, args.workers, args.progress)
