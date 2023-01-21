from pathlib import Path

import pytest
from dynaconf import Dynaconf


def test_merge(config: Dynaconf, envvar_url: bool, envvar_connect_args: bool):
    """Confirm how merging works

    https://www.dynaconf.com/merging/

    It was originally developed to check when overriding db.url would delete
    db.connect_args.check_same_thread.

    Note that the check_same_thread option can be provided as part of url.
    https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#uri-connections

    """
    if envvar_url:
        assert "sqlite:///env.sqlite3" == config.db.url
    else:
        assert "sqlite:///config.sqlite3" == config.db.url

    if envvar_connect_args:
        assert {"check_same_thread": True} == config.db.connect_args
    elif envvar_connect_args is None:
        assert {} == config.db.connect_args
    else:
        assert {"check_same_thread": False} == config.db.connect_args


@pytest.fixture
def config():
    here = Path(__file__).resolve().parent
    ret = Dynaconf(
        envvar_prefix="NEXTLINE",
        settings_files=[
            str(here / 'default.toml'),
            str(here / 'config.toml'),
        ],
        # environments=True,  # enable sections, e.g., "development"
    )
    return ret


@pytest.fixture(params=[True, False])
def envvar_url(request, monkeypatch):
    if ret := request.param:
        monkeypatch.setenv("NEXTLINE_DB__URL", "sqlite:///env.sqlite3")
        # dunder merging
        # https://www.dynaconf.com/merging/#dunder-merging-for-nested-structures
    return ret


@pytest.fixture(params=[False, True, None])
def envvar_connect_args(request, monkeypatch):
    # False: intact
    # True: override
    # None: remove
    if ret := request.param:
        monkeypatch.setenv(
            "NEXTLINE_DB__CONNECT_ARGS",
            "{check_same_thread=true}",
        )
    elif ret is None:
        monkeypatch.setenv(
            "NEXTLINE_DB__connect_args__check_same_thread",
            "@del",
        )
    return ret
