import os
import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative


postgres_host = os.environ.get("POSTGRES_HOST")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_port = os.environ.get("POSTGRES_PORT")

DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}" + \
    f"@{postgres_host}:{postgres_port}/{postgres_db}"

engine = _sql.create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = _sql.orm.sessionmaker(autocommit=False,
                                     autoflush=False, bind=engine)
Base = _declarative.declarative_base()
