from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import date


class SentimentsEnum(str, Enum):
    """
    Enum para classificação de sentimentos de avaliações de clientes.

    Esta classe define os valores de sentimentos possíveis para
    atribuição às avaliações de clientes após análise de texto.

    Attributes:
        POSITIVE (str): Representa avaliações com sentimento positivo.
            Valor: "positive"
        NEUTRAL (str): Representa avaliações com sentimento neutro.
            Valor: "neutral"
        NEGATIVE (str): Representa avaliações com sentimento negativo.
            Valor: "negative"

    Example:
        >>> sentiment = SentimentsEnum.POSITIVE
        >>> print(sentiment)
        positive
        >>> print(sentiment.value)
        positive
        >>> isinstance(sentiment, str)
        True
    """

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ReviewBase(BaseModel):
    """
    Schema base para dados de avaliação de clientes.

    Contém campos essenciais para registro e validação de uma avaliação
    de cliente, incluindo nome, texto da avaliação e data.

    Atributos:
        customer_name (str): Nome do cliente autor da avaliação.
        review_text (str): Texto completo da avaliação do cliente.
        evaluation_date (date): Data da avaliação.
    """

    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do cliente autor da avaliação",
        example="Miriam Duarte"
    )

    review_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texto completo da avaliação do cliente",
        example="O atendimento foi rápido, mas poderia ser mais detalhado."
    )

    evaluation_date: date = Field(
        ...,
        description="Data em que a avaliação feita",
        example="2025-07-17"
    )

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v: str) -> str:
        """Valida e limpa o nome do cliente."""
        if not v.strip():
            raise ValueError("Nome do cliente não pode estar vazio")
        return v.strip()

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        """Valida e limpa o texto da avaliação."""
        if not v.strip():
            raise ValueError("Texto da avaliação não pode estar vazio")
        return v.strip()

    @field_validator("evaluation_date")
    @classmethod
    def validate_evaluation_date(cls, v: date) -> date:
        """Garante que a data da avaliação não seja futura."""
        if v > date.today():
            raise ValueError("Data da avaliação não pode ser futura")
        return v
