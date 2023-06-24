from setuptools import setup, find_packages

setup(
    name="seqsleuth",
    version="0.2.0",
    description="A sequencing technology metadata extraction tool.",
    author="ND Olson",
    author_email="nolson@nist.gov",
    url="http://github.com/nate-d-olson/seqsleuth",
    packages=find_packages(),
    install_requires=["pysam"],
    entry_points={
        "console_scripts": [
            "seqsleuth=seqsleuth.main:__main__",  # replace this with your actual module and function
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
