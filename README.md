# nextline-graphql

_The plugin-based framework of a Python API server._

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
  - [Backend API server (Python)](#backend-api-server-python)
    - [Core package](#core-package)
    - [Plugin system](#plugin-system)
    - [Plugins](#plugins)
    - [Utility](#utility)
  - [Frontend web app (TypeScript)](#frontend-web-app-typescript)
- [How to run the Nextline backend API server](#how-to-run-the-nextline-backend-api-server)
  - [As a Docker container](#as-a-docker-container)
  - [In a virtual environment](#in-a-virtual-environment)
- [Configuration](#configuration)
  - [CORS](#cors)
  - [Logging](#logging)
  - [`graphql` plugin](#graphql-plugin)
  - [`ctrl` plugin](#ctrl-plugin)
- [Check out code for development](#check-out-code-for-development)

## Introduction

This package provides the framework for a plugin-based Python API server.
Plugins can implement endpoints and services.

This framework was originally developed as part of _Nextline_, a DAQ sequencer
of the [Observatory Control System (OCS)](https://github.com/simonsobs/ocs/),
which allows line-by-line execution of concurrent Python scripts, which control
telescopes, by multiple users simultaneously from web browsers.

## Citation

Please use the following DOI for [the core
package](https://github.com/simonsobs/nextline) to cite Nextline in general
unless you need to refer to a specific package.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11451619.svg)](https://doi.org/10.5281/zenodo.11451619)

## Packages

Nextline consists of multiple packages. This package, _nextline-graphql_,
provides the framework for the backend API server.

| Package                                                                                   | Language   | Release                                                                                                                  | Build                                                                                                                                                                                          | Coverage                                                                                                                                           |
| :---------------------------------------------------------------------------------------- | ---------- | :----------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------- |
| [**nextline**](https://github.com/simonsobs/nextline)                                     | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline.svg)](https://pypi.org/project/nextline)                       | [![Test Status](https://github.com/simonsobs/nextline/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline/actions/workflows/unit-test.yml)                       |                                                                                                                                                    |
| [**apluggy**](https://github.com/simonsobs/apluggy)                                       | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/apluggy.svg)](https://pypi.org/project/apluggy)                         | [![Test Status](https://github.com/simonsobs/apluggy/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/apluggy/actions/workflows/unit-test.yml)                         | [![codecov](https://codecov.io/gh/simonsobs/apluggy/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/apluggy)                         |
| [**nextline&#x2011;graphql**](https://github.com/simonsobs/nextline-graphql)              | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline-graphql.svg)](https://pypi.org/project/nextline-graphql)       | [![Test Status](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-graphql/actions/workflows/unit-test.yml)       | [![codecov](https://codecov.io/gh/simonsobs/nextline-graphql/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-graphql)       |
| [**nextline&#x2011;rdb**](https://github.com/simonsobs/nextline-rdb)                      | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline-rdb.svg)](https://pypi.org/project/nextline-rdb)               | [![Test Status](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-rdb/actions/workflows/unit-test.yml)               | [![codecov](https://codecov.io/gh/simonsobs/nextline-rdb/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-rdb)               |
| [**nextline&#x2011;schedule**](https://github.com/simonsobs/nextline-schedule)            | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline-schedule.svg)](https://pypi.org/project/nextline-schedule)     | [![Test Status](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml)     | [![codecov](https://codecov.io/gh/simonsobs/nextline-schedule/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-schedule)     |
| [**nextline&#x2011;alert**](https://github.com/simonsobs/nextline-alert)                  | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline-alert.svg)](https://pypi.org/project/nextline-alert)           | [![Test Status](https://github.com/simonsobs/nextline-alert/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-alert/actions/workflows/unit-test.yml)           | [![codecov](https://codecov.io/gh/simonsobs/nextline-alert/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-alert)           |
| [**nextline&#x2011;test&#x2011;utils**](https://github.com/simonsobs/nextline-test-utils) | Python     | [![PyPI - Version](https://img.shields.io/pypi/v/nextline-test-utils.svg)](https://pypi.org/project/nextline-test-utils) | [![Test Status](https://github.com/simonsobs/nextline-test-utils/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-test-utils/actions/workflows/unit-test.yml) | [![codecov](https://codecov.io/gh/simonsobs/nextline-test-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-test-utils) |
| [**nextline&#x2011;web**](https://github.com/simonsobs/nextline-web)                      | TypeScript | [![npm](https://img.shields.io/npm/v/nextline-web)](https://www.npmjs.com/package/nextline-web)                          | [![Unit tests](https://github.com/simonsobs/nextline-web/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-web/actions/workflows/unit-test.yml)                |                                                                                                                                                    |

### Backend API server (Python)

#### Core package

- [**nextline:**](https://github.com/simonsobs/nextline) The core functionality
  of Nextline. It controls the execution of the Python scripts. It is used by
  the plugin _ctrl_.

#### Plugin system

The plugin system of _nextline-graphql_ is _apluggy_.

- [**apluggy:**](https://github.com/simonsobs/apluggy) A wrapper of
  [pluggy](https://pluggy.readthedocs.io/) to support asyncio and context
  managers.

#### Plugins

##### Internal plugins

These plugins are included in this package.

- [**graphql:**](./nextlinegraphql/plugins/graphql/) The entry point of the
  GraphQL API, implemented with [strawberry-graphql](https://strawberry.rocks/).
- [**ctrl:**](./nextlinegraphql/plugins/ctrl/) The core plugin that controls
  the execution of the Python scripts. It uses the package
  [_nextline_](https://github.com/simonsobs/nextline).

##### External plugins

These plugins are not included in this package. They can be installed separately.

- [**nextline-rdb:**](https://github.com/simonsobs/nextline-rdb) A relational database for nextline. It stores configuration, execution history, and other information. It is implemented with [SQLAlchemy 2](https://www.sqlalchemy.org/).
- [**nextline-schedule:**](https://github.com/simonsobs/nextline-schedule) The **auto mode**. The **queue system**. An interface to the [_SO scheduler_](https://github.com/simonsobs/scheduler).
- [**nextline-alert:**](https://github.com/simonsobs/nextline-alert) An interface to the alert system [_campana_](https://github.com/simonsobs/campana).

#### Utility

- [**nextline-test-utils:**](https://github.com/simonsobs/nextline-test-utils)
  A collection of test utilities for backend development

### Frontend web app (TypeScript)

The frontend web app is currently in a single package. The development of a
plugin-based system is planned.

- [**nextline-web:**](https://github.com/simonsobs/nextline-web)
  The frontend web app of Nextline. It is a Vue.js app.

## How to run the Nextline backend API server

The section shows how to run the Nextline backend API server. How to run the
frontend web app is described
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
management. nextline-graphql itself has configuration for CORS and logging. The
internal plugin `ctrl` also has configurations. External plugins can extend the
configuration.

### CORS

These CORS (Cross-Origin Resource Sharing) settings will be given to
`allow_origin` and `allow_headers` of Starlette's
[`CORSMiddleware`](https://www.starlette.io/middleware/#corsmiddleware).

| Environment variable               | Default value | Description                                                                                                                                                                                                                                                                                                                               |
| ---------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `NEXTLINE_CORS__ALLOW_ORIGINS`     | `['*']`       | A list of allowed origins, e.g., `["http://example.com:8080"]`. The default value (`"*"`) allows any origins.                                                                                                                                                                                                                             |
| `NEXTLINE_CORS__ALLOW_HEADERS`     | `['*']`       | A list of allowed HTTP request headers. For example, `['remote-user', 'remote-name', 'remote-email']` can be appropriate values if Authelia is used. Some headers such as `Content-Type` are always allowed (See [the Starlette doc](https://www.starlette.io/middleware/#corsmiddleware)). The default value (`"*"`) allows any headers. |
| `NEXTLINE_CORS__ALLOW_CREDENTIALS` | `false`       | Whether to support cookies. If `true`, the wildcard (`"*"`) cannot be used for `NEXTLINE_CORS__ALLOW_ORIGINS` or `NEXTLINE_CORS__ALLOW_HEADERS`. They need to be listed explicitly.                                                                                                                                                       |

### Logging

See [`default.toml`](./nextlinegraphql/config/default.toml).

### `graphql` plugin

| Environment variable                       | Default value | Description                                                                                      |
| ------------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------ |
| `NEXTLINE_GRAPHQL__MUTATION_ALLOW_ORIGINS` | `[*]`         | A list of allowed origins for GraphQL Mutations. The default value (`"*"`) allows any origins.\* |

- In addition to the CORS settings above, this setting provides further access control for
  GraphQL Mutations. With this setting, you can allow only GraphQL Queries and Subscriptions from
  certain origins while prohibiting Mutations.

### `ctrl` plugin

| Environment variable           | Default value | Description                                                                                                                                 |
| ------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `NEXTLINE_CTRL__TRACE_MODULES` | `false`       | By default (`false`), Nextline only traces the main Python script. If `true`, Nextline traces execution of imported Python modules as well. |
| `NEXTLINE_CTRL__TRACE_THREADS` | `false`       | By default (`false`), Nextline only traces the main thread. If `true`, Nextline traces execution of other threads as well.                  |

## Check out code for development

How to check out code from GitHub for development:

```bash
git clone git@github.com:simonsobs/nextline-graphql.git
cd nextline-graphql/
python -m venv venv
source venv/bin/activate
pip install -e ./"[tests,dev]"
```

To run

```bash
uvicorn --port 8080 --lifespan on --factory --reload nextlinegraphql:create_app
```
