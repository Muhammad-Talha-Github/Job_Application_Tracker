from logging.config import fileConfig

from alembic import context

from app.database import DATABASE_URL, Base, engine
from app import models  # noqa: F401 - importing registers models on Base.metadata


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic compares migrations with the same model definitions used by FastAPI.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Create migration SQL without opening a database connection."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the configured SQLAlchemy engine connection."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
