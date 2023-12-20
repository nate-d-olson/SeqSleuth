from setuptools import setup, find_packages
from seqsleuth import version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="seqsleuth",
    version=version.__version__,
    description="A sequencing technology metadata extraction tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ND Olson",
    author_email="nolson@nist.gov",
    platforms="any",
    url="http://github.com/nate-d-olson/seqsleuth",
    project_urls={
        "Documentation": "https://github.com/nate-d-olson/seqsleuth/wiki",
        "Source": "https://github.com/nate-d-olson/seqsleuth",
        "Tracker": "https://github.com/nate-d-olson/seqsleuth/issues",
    },
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=["pysam", "tqdm"],
    entry_points={
        "console_scripts": [
            "seqsleuth=seqsleuth.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
)
