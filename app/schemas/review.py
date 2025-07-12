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
        """
        Valida o campo customer_name, garantindo que não esteja vazio ou só
        com espaços.

        Args:
            v (str): Nome do cliente.

        Returns:
            str: Nome do cliente validado.

        Raises:
            ValueError: Se o nome estiver vazio ou contiver apenas espaços.
        """
        if not v.strip():
            raise ValueError("Nome do cliente não pode estar vazio")
        return v.strip()

    @field_validator("review_text")
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        """
        Valida o campo review_text, garantindo que não esteja vazio ou só
        com espaços.

        Args:
            v (str): Texto da avaliação.

        Returns:
            str: Texto da avaliação validado.

        Raises:
            ValueError: Se o texto estiver vazio ou contiver apenas espaços.
        """
        if not v.strip():
            raise ValueError("Texto da avaliação não pode estar vazio")
        return v.strip()

    @field_validator("evaluation_date")
    @classmethod
    def validate_evaluation_date(cls, v: date) -> date:
        """
        Valida a data da avaliação, garantindo que não seja uma data futura.

        Args:
            v (date): Data da avaliação.

        Returns:
            date: Data validada.

        Raises:
            ValueError: Se a data estiver no futuro.
        """
        if v > date.today():
            raise ValueError("Data da avaliação não pode ser futura")
        return v


class ReviewCreate(ReviewBase):
    """
    Schema para criação de avaliações de clientes.

    Herda todos os campos e validações de ReviewBase. Utilizado como modelo
    de entrada para o endpoint de criação de avaliações.
    """
    pass


class ReviewResponse(BaseModel):
    """
    Schema de resposta para avaliações de clientes.

    Representa os dados retornados pela API ao consultar ou criar uma
    avaliação, incluindo o identificador único, timestamps e o sentimento
    classificado.

    Attributes:
        id (int): Identificador único da avaliação.
        customer_name (str): Nome do cliente autor da avaliação.
        review_text (str): Texto completo da avaliação.
        evaluation_date (date): Data original da avaliação.
        created_at (datetime): Data e hora de criação do registro no sistema.
        updated_at (datetime): Data e hora da última atualização do registro.
        sentiment (SentimentsEnum): Sentimento classificado da avaliação.
    """

    id: int = Field(..., example=1)
    customer_name: str = Field(
        ...,
        example="Ana Silva"
    )

    review_text: str = Field(
        ...,
        example="O atendimento foi excelente e resolveu meu problema."
    )

    evaluation_date: date = Field(
        ...,
        example="2025-07-10"
    )

    sentiment: SentimentsEnum = Field(
        ...,
        example="positive"
    )
