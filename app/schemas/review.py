from enum import Enum


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
