"""
Setup script for Packet Tracer Mark Scanner

Version: 0.1
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="packet-tracer-mark-scanner",
    version="0.1.0",
    author="askbard",
    author_email="",
    description="A comprehensive toolkit for automating Cisco Packet Tracer (PKA) file processing and mark extraction",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/askbard/packetracermark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pka-launcher=run:main",
            "pka-capture=scripts.pka_capture:main",
            "pka-scanner=scripts.mark_scanner:main",
            "pka-validate=scripts.validate_setup:main",
            "pka-batch=scripts.batch_process:main",
        ],
    },
    keywords="cisco packet-tracer ocr education automation screenshot",
    project_urls={
        "Bug Reports": "https://github.com/askbard/packetracermark/issues",
        "Source": "https://github.com/askbard/packetracermark",
        "Documentation": "https://github.com/askbard/packetracermark#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
