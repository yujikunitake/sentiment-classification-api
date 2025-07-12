"""Configuração do banco de dados e sessão para a aplicação."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Provedor de sessão do banco de dados para injeção no FastAPI.

    Yields:
        Session: Sessão do banco de dados SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
