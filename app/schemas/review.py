from enum import Enum
from pydantic import BaseModel, Field
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
    custmer_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Nome do cliente autor da avaliação",
        examples="Miriam Duarte"
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
