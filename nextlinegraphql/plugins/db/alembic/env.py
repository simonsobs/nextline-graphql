import logging
import logging.config

from alembic import context
from sqlalchemy import create_engine

from nextlinegraphql.config import create_settings
from nextlinegraphql.plugins.db import models

settings = create_settings()

# Config in alembic.ini, only used to configure logger
config = context.config

# E.g., how to access to a config value
# script_location = config.get_main_option("script_location")

if config.config_file_name:
    # from logging_tree import printout
    # printout()
    if "nextlinegraphql" not in logging.root.manager.loggerDict:
        # Presumably, the alembic command is being executed. If programmatically
        # called, "nextlinegraphql" is in loggerDict and logging shouldn't be
        # configured here because it will override the logging configuration.
        # TODO: rearrange how configuration files are read so that this
        # conditional configuration of logging becomes cleaner or deleted.
        logging.config.fileConfig(config.config_file_name)

target_metadata = models.Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.db.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(settings.db.url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
