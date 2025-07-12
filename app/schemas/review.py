"""Schemas Pydantic para avaliações de clientes."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class SentimentsEnum(str, Enum):
    """Enum para classificação de sentimentos."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ReviewBase(BaseModel):
    """Schema base para dados de avaliação de clientes."""

    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do cliente",
        json_schema_extra={"example": "Miriam Kunitake"},
    )

    review_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texto da avaliação",
        json_schema_extra={"example": "O atendimento foi rápido."},
    )

    evaluation_date: date = Field(
        ...,
        description="Data da avaliação",
        json_schema_extra={"example": "2024-07-17"},
    )

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v: str) -> str:
        """Valida que o nome não está vazio ou só com espaços."""
        if not v.strip():
            raise ValueError("Nome do cliente não pode estar vazio")
        return v.strip()

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        """Valida que o texto não está vazio ou só com espaços."""
        if not v.strip():
            raise ValueError("Texto da avaliação não pode estar vazio")
        return v.strip()

    @field_validator("evaluation_date")
    @classmethod
    def validate_evaluation_date(cls, v: date) -> date:
        """Valida que a data não está no futuro."""
        if v > date.today():
            raise ValueError("Data da avaliação não pode ser futura")
        return v


class ReviewCreate(ReviewBase):
    """Schema para criação de avaliações."""
    pass


class ReviewResponse(BaseModel):
    """Schema de resposta para avaliações da API."""

    id: int = Field(..., json_schema_extra={"example": 1})

    customer_name: str = Field(
        ..., json_schema_extra={"example": "Mariana Miranda"}
    )

    review_text: str = Field(
        ...,
        json_schema_extra={
            "example": "O atendimento resolveu meu problema."
        },
    )

    evaluation_date: date = Field(
        ..., json_schema_extra={"example": "2024-07-28"}
    )

    sentiment: SentimentsEnum = Field(
        ..., json_schema_extra={"example": "positive"}
    )
