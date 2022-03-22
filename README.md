[![PyPI version](https://badge.fury.io/py/nextline-graphql.svg)](https://badge.fury.io/py/nextline-graphql)
[![Test Status](https://github.com/simonsobs/nextline-graphql/workflows/Test/badge.svg)](https://github.com/simonsobs/nextline-graphql/actions?query=workflow%3ATest)
[![codecov](https://codecov.io/gh/simonsobs/nextline-graphql/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-graphql)

# nextline-graphql

A GraphQL API for Nextline

_Nextline_ allows line-by-line execution of concurrent Python scripts by
multiple users simultaneously from web browsers. Nextline is being developed as
a DAQ sequencer of the [Observatory Control System
(OCS)](https://github.com/simonsobs/ocs/).

## Packages

- [**nextline:**](https://github.com/simonsobs/nextline) (Python) the core functionality. imported in _nextline-graphql._
- [**nextline-graphql:**](https://github.com/simonsobs/nextline-graphql) (Python) this package. the GraphQL API
- [**nextline-web:**](https://github.com/simonsobs/nextline-web) (JavaScript) the client website

## How to run the Nextline GraphQL API

The section shows how to run the Nextline GraphQL API server. How to run the
client website will be described
[elsewhere](https://github.com/simonsobs/nextline-web).

### As a Docker container

Docker images of the Nextline GraphQL API server are created as
[ghcr.io/simonsobs/nextline-graphql](https://github.com/simonsobs/nextline-graphql/pkgs/container/nextline-graphql).
These images are created by the
[Dockerfile](https://github.com/simonsobs/nextline-graphql/blob/main/Dockerfile).

Use, for example, the following command to run as a Docker container.

```bash
docker run -p 8080:8000 ghcr.io/simonsobs/nextline-graphql
```

If you access to the API server with a web browser, you will see the GraphQL IDE: <http://localhost:8080/>.

### With a persistent DB

Nextline-graphql stores the execution history and other information in the DB.
It uses [SQLAlchemy](https://www.sqlalchemy.org/), with, by default, a [SQLite
in-memory database](https://www.sqlite.org/inmemorydb.html).

#### An environment variable in the container

The container has one environment variable, which is to change the [DB URL](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) of SQLAlchemy.

| Environment variable | Default value                                | Description                                                                                   |
| -------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `NEXTLINE_DB__URL`   | `sqlite:///:memory:?check_same_thread=false` | The [DB URL](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) of SQLAlchemy |

For example, the following command uses a file on the host machine
`db/db.sqlite3` as the persistent DB. The directory `db/` and the file
`db.sqlite3` will be created if they don't exist.

```bash
docker run -p 8080:8000 --env NEXTLINE_DB__URL='sqlite:////db/db.sqlite3' -v "$(pwd)/db:/db" ghcr.io/simonsobs/nextline-graphql
```

### from PyPI

It is also possible to install with pip and run.

```bash
pip install nextline-graphql
uvicorn --lifespan on --factory --port 8080 nextlinegraphql:create_app
```

The environment variable `NEXTLINE_DB__URL` mentioned above can be used to
specify the SQLAlchemy DB URL.

Check with a web browser at <http://localhost:8080/>.

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

---

## License

- _Nextline_ is licensed under the MIT license.

---

## Contact

- [Tai Sakuma](https://github.com/TaiSakuma) <span itemscope itemtype="https://schema.org/Person"><a itemprop="sameAs" content="https://orcid.org/0000-0003-3225-9861" href="https://orcid.org/0000-0003-3225-9861" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:text-top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon"></a></span>
