from setuptools import setup, find_packages
import versioneer

from pathlib import Path

here = Path(__file__).resolve().parent
long_description = here.joinpath("README.md").read_text()

setup(
    name="nextline-graphql",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A GraphQL API for Nextline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Simons Observatory",
    author_email="so_software@simonsobservatory.org",
    url="https://github.com/simonsobs/nextline",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    install_requires=[
        "nextline>=0.0.3",
        "ariadne>=0.12.0",
        "uvicorn>=0.12.2",
        "websockets>=8.1",
        "janus>=0.6",
        "SQLAlchemy>=1.4",
    ],
    extras_require={
        "tests": [
            "pytest>=5.4",
            "pytest-cov>=2.8",
            "pytest-asyncio>=0.14",
            "snapshottest>0.5",
            "async-asgi-testclient>=1.4.6",
        ],
        "dev": [
            "uvicorn",
            "twine",
            "flake8",
            "black",
        ],
    },
)
