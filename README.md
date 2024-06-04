# nextline-graphql

_The plugin-based framework of the Nextline backend API server_

---

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-graphql.svg)](https://pypi.org/project/nextline-graphql)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-graphql.svg)](https://pypi.org/project/nextline-graphql)

[![Test Status](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test-dev.yml/badge.svg)](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-graphql/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-graphql/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-graphql/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-graphql)

---

**Table of Contents**

- [Introduction](#introduction)
- [Citation](#citation)
- [Packages](#packages)
  - [Core package](#core-package)
  - [Plugin system](#plugin-system)
  - [Plugins](#plugins)
    - [Internal plugins](#internal-plugins)
    - [External plugins](#external-plugins)
  - [Web App](#web-app)
- [How to run the Nextline backend API server](#how-to-run-the-nextline-backend-api-server)
  - [As a Docker container](#as-a-docker-container)
  - [In a virtual environment](#in-a-virtual-environment)
- [Configuration](#configuration)
- [Check out code for development](#check-out-code-for-development)

## Introduction

_Nextline_ is a DAQ sequencer of the [Observatory Control System
(OCS)](https://github.com/simonsobs/ocs/). Nextline allows line-by-line
execution of concurrent Python scripts, which control telescopes, by multiple
users simultaneously from web browsers.

Nextline consists of multiple packages. This package, _nextline-graphql_, provides the
framework for the backend API server. It is a plugin-based framework. Features
are added by plugins.

## Citation

Please use the following DOI for [the core
package](https://github.com/simonsobs/nextline) to cite Nextline in general
unless you need to refer to a specific package.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11451619.svg)](https://doi.org/10.5281/zenodo.11451619)


## Packages

### Core package

- [**nextline:**](https://github.com/simonsobs/nextline) The core functionality
  of Nextline. It controls the execution of the Python scripts. It is used by
  the plugin _ctrl_.

### Plugin system

The plugin system of _nextline-graphql_ is _apluggy_.

- [**apluggy:**](https://github.com/simonsobs/apluggy) A wrapper of
  [pluggy](https://pluggy.readthedocs.io/) to support asyncio and context
  managers.

### Plugins

#### Internal plugins

These plugins are included in this package.

- [**graphql:**](./nextlinegraphql/plugins/graphql/) The entry point of the
  GraphQL API, implemented with [strawberry-graphql](https://strawberry.rocks/).
- [**ctrl:**](./nextlinegraphql/plugins/ctrl/) The core plugin that controls
  the execution of the Python scripts. It uses the package
  [_nextline_](https://github.com/simonsobs/nextline).

#### External plugins

These plugins are not included in this package. They can be installed separately.

- [**nextline-rdb:**](https://github.com/simonsobs/nextline-rdb) A relational database for nextline. It stores configuration, execution history, and other information. It is implemented with [SQLAlchemy 2](https://www.sqlalchemy.org/).
- [**nextline-schedule:**](https://github.com/simonsobs/nextline-schedule) An interface to the [_SO scheduler_](https://github.com/simonsobs/scheduler).
- [**nextline-alert:**](https://github.com/simonsobs/nextline-alert) An interface to the alert system [_campana_](https://github.com/simonsobs/campana).

### Web App

The front-end web app is currently in a single package. The development of a
plugin-based system is planned.

- [**nextline-web:**](https://github.com/simonsobs/nextline-web) (TypeScript)
  The front-end web app of Nextline. It is a Vue.js app.

## How to run the Nextline backend API server

The section shows how to run the Nextline backend API server. How to run the
front-end web app is described
[elsewhere](https://github.com/simonsobs/nextline-web).

### As a Docker container

Docker images of the Nextline backend API server are created as
[ghcr.io/simonsobs/nextline-graphql](https://github.com/simonsobs/nextline-graphql/pkgs/container/nextline-graphql).
These images are created by the
[Dockerfile](https://github.com/simonsobs/nextline-graphql/blob/main/Dockerfile).
No external plugins are included in the images.

Use, for example, the following command to run as a Docker container.

```bash
docker run -p 8080:8000 ghcr.io/simonsobs/nextline-graphql
```

If you access to the API server with a web browser, you will see the GraphQL
IDE: <http://localhost:8080/>.

To include external plugins, you can create a new Docker image with
_ghcr.io/simonsobs/nextline-graphql_ as the base image. For example,
[nextline-rdb](https://github.com/simonsobs/nextline-rdb) shows how to create a
new Docker image with _nextline-rdb_ as an external plugin.

### In a virtual environment

You can create a virtual environment, install packages, and run the API server
as follows.

```bash
python -m venv venv
source venv/bin/activate
pip install nextline-graphql
pip install uvicorn
uvicorn --lifespan on --factory --port 8080 nextlinegraphql:create_app
```

Check with a web browser at <http://localhost:8080/>.

If you check out external plugins, nextline-graphql automatically detects them
as plugins. An example can be described in
[nextline-rdb](https://github.com/simonsobs/nextline-rdb).

## Configuration

nextline-graphql uses [dynaconf](https://www.dynaconf.com/) for configuration
management. nextline-graphql itself does not have any configuration except for
logging. External plugins have configurations.

## Check out code for development

This section shows an example way to check out code from GitHub for development.

```bash
python -m venv venv
source venv/bin/activate
git clone git@github.com:simonsobs/nextline.git
git clone git@github.com:simonsobs/nextline-graphql.git
pip install -e ./nextline/"[tests,dev]"
pip install -e ./nextline-graphql/"[tests,dev]"
```

To run

```bash
uvicorn --port 8080 --lifespan on --factory --reload --reload-dir nextline-graphql --reload-dir nextline nextlinegraphql:create_app
```
