from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
from app.schemas.review import SentimentsEnum


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
            Integer,
            primary_key=True,
            index=True
        )
    customer_name = Column(
            String(255),
            nullable=False,
            index=True
        )
    review_text = Column(
            Date,
            nullable=False,
            index=True
        )
    evaluation_date = Column(
        Date,
        nullable=False,
        index=True
    )
    created_at = Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            index=True
        )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    sentiment = Column(
        Enum(
            SentimentsEnum,
            name="sentiments_enum",
            create_type=True
        ),
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        """
        Representação em string do objeto de Review

        Returns:
            str: Representação legível do objeto contendo ID, cliente,
                data da avaliação e sentimento.
        """
        return (
            f"<Review(id={self.id}, customer='{self.customer_name}', "
            f"sentiment='{self.sentiment.value}', date='{self.evaluation_date}'"  # noqa: E501
        )
