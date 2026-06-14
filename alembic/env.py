"""
Alembic Environment Configuration

This file is used by Alembic to:
1. Connect to the database
2. Read SQLAlchemy models
3. Generate and apply migrations

Alembic tracks schema versions like Git tracks code changes.
Each migration is like a Git commit - it records what changed.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# FIX: Correctly trace and bind the system search paths for root execution
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# Import our application's database configuration
from app.config import settings
from app.database import Base

# Import ALL models so Alembic can detect them
# These must be imported explicitly for autogenerate to work
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review

# Alembic Config object
config = context.config

# Override sqlalchemy.url with our application settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
# Base.metadata contains all table definitions from our models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    Configures the context with just a URL and not an Engine.
    Calls to context.execute() emit SQL to the script output.
    
    Use this mode when you want to generate SQL scripts without
    connecting to the database.
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


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    Creates an Engine and associates a connection with the context.
    This is the standard way to apply migrations to your database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Run migrations in the appropriate mode
if context.is_offline_mode():
    print("📝 Running Alembic migrations OFFLINE (generating SQL)")
    run_migrations_offline()
else:
    print("🔨 Running Alembic migrations ONLINE (applying to database)")
    run_migrations_online()
