# nextline-graphql

(This package will be renamed in the future.)

_Python framework for building plugin‑based HTTP API servers._

---

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-graphql.svg)](https://pypi.org/project/nextline-graphql)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-graphql.svg)](https://pypi.org/project/nextline-graphql)

[![Test Status](https://github.com/nextline-dev/nextline-graphql/actions/workflows/unit-test.yml/badge.svg)](https://github.com/nextline-dev/nextline-graphql/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/nextline-dev/nextline-graphql/actions/workflows/type-check.yml/badge.svg)](https://github.com/nextline-dev/nextline-graphql/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/nextline-dev/nextline-graphql/branch/main/graph/badge.svg)](https://codecov.io/gh/nextline-dev/nextline-graphql)

---

**Table of Contents**

- [Introduction](#introduction)
- [How to run](#how-to-run)
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

(This package will not be specific to Nextline or GraphQL and will be renamed in the future.)

## How to run

The section shows how to run the Nextline backend API server. How to run the
frontend web app is described
[elsewhere](https://github.com/nextline-dev/nextline-web).

### As a Docker container

Docker images of the Nextline backend API server are created as
[ghcr.io/nextline-dev/nextline-graphql](https://github.com/nextline-dev/nextline-graphql/pkgs/container/nextline-graphql).
These images are created by the
[Dockerfile](https://github.com/nextline-dev/nextline-graphql/blob/main/Dockerfile).
No external plugins are included in the images.

Use, for example, the following command to run as a Docker container.

```bash
docker run -p 8080:8000 ghcr.io/nextline-dev/nextline-graphql
```

If you access to the API server with a web browser, you will see the GraphQL
IDE: <http://localhost:8080/>.

To include external plugins, you can create a new Docker image with
_ghcr.io/nextline-dev/nextline-graphql_ as the base image. For example,
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
management. The nextline-graphql framework itself has configuration for CORS
and logging. The internal plugins have configurations. External plugins can
extend the configuration.

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
git clone git@github.com:nextline-dev/nextline-graphql.git
cd nextline-graphql/
python -m venv venv
source venv/bin/activate
pip install -e ./"[tests,dev]"
```

To run

```bash
uvicorn --port 8080 --lifespan on --factory --reload nextlinegraphql:create_app
```
