from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config,pool
from config import DATABASE_URL
from database.models import Base
config=context.config
if config.config_file_name:fileConfig(config.config_file_name)
config.set_main_option('sqlalchemy.url',str(DATABASE_URL).replace('%','%%'))
target_metadata=Base.metadata
def offline():
 context.configure(url=config.get_main_option('sqlalchemy.url'),target_metadata=target_metadata,literal_binds=True,dialect_opts={'paramstyle':'named'});context.run_migrations()
def online():
 c=engine_from_config(config.get_section(config.config_ini_section),prefix='sqlalchemy.',poolclass=pool.NullPool)
 with c.connect() as connection:
  context.configure(connection=connection,target_metadata=target_metadata);context.run_migrations()
if context.is_offline_mode():offline()
else:online()
