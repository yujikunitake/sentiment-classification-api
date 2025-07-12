"""Modelo ORM para a tabela de avaliações (reviews)."""

from sqlalchemy import Column, Date, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.database import Base
from app.schemas.review import SentimentsEnum


class Review(Base):
    """Representa uma avaliação de cliente no banco de dados."""

    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    customer_name = Column(
        String(255),
        nullable=False,
        index=True,
    )
    review_text = Column(
        String(5000),
        nullable=False,
        index=True,
    )
    evaluation_date = Column(
        Date,
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    sentiment = Column(
        Enum(
            SentimentsEnum,
            name="sentiments_enum",
            create_type=True,
        ),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        """Representação legível do objeto Review."""
        return (
            f"<Review(id={self.id}, customer='{self.customer_name}', "
            f"sentiment='{self.sentiment.value}', "
            f"date='{self.evaluation_date}')>"
        )
