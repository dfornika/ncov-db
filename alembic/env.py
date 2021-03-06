from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
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
    # 2021-08-26 dfornika
    # replaced default implementation (commented out below)
    # with the implementation from here:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#sharing-a-connection-with-a-series-of-migration-commands-and-environments
    # in order to get tests working with in-memory db
    db_path = context.get_x_argument(as_dictionary=True).get('db')
    if db_path:
        ini_section = config.get_section(config.config_ini_section, 'alembic')
        ini_section['sqlalchemy.url'] = db_path

    connectable = config.attributes.get('connection', None)

    if connectable is None:
        # only create Engine if we don't have a Connection
        # from the outside
        db_path = context.get_x_argument(as_dictionary=True).get('db')
        if db_path:
            ini_section = config.get_section(config.config_ini_section)
            ini_section['sqlalchemy.url'] = db_path
        connectable = engine_from_config(
            ini_section,
            prefix='sqlalchemy.',
            poolclass=pool.NullPool
        )

    # when connectable is already a Connection object, calling
    # connect() gives us a *branched connection*.

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

    #connectable = engine_from_config(
    #    config.get_section(config.config_ini_section),
    #    prefix="sqlalchemy.",
    #    poolclass=pool.NullPool,
    #)
    #
    #with connectable.connect() as connection:
    #    context.configure(
    #        connection=connection, target_metadata=target_metadata
    #    )
    #
    #    with context.begin_transaction():
    #        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
