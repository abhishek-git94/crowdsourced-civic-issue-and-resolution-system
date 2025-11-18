import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL missing')


engine = create_engine(
DATABASE_URL,
future=True,
pool_pre_ping=True,
connect_args={"connect_timeout": 10},
pool_size=5,
max_overflow=10,
)


SessionLocal = sessionmaker(
bind=engine,
autoflush=False,
autocommit=False,
expire_on_commit=False,
future=True,
)


print('SQLAlchemy engine ready to go!')