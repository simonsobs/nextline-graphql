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
        "nextline>=0.1.11",
        "strawberry-graphql>=0.103",
        "starlette==0.16.0",
        "websockets>=10.2",
        "janus>=0.6",
        "SQLAlchemy>=1.4",
        "alembic>=1.7",
        "dynaconf>=3.1",
    ],
    extras_require={
        "tests": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "pytest-asyncio>=0.18",
            "pytest-timeout>=2.1",
            "snapshottest>=0.6",
            "async-asgi-testclient>=1.4",
        ],
        "dev": [
            "tox",
            "twine",
            "flake8",
            "black",
            "mypy",
            "sqlalchemy-stubs",
            "logging_tree",
            "uvicorn",
        ],
    },
)
