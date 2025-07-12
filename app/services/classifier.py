from flair.models import TextClassifier
from flair.data import Sentence
from typing import Dict, List


class SentimentClassifier:
    """
    Classificador de sentimentos que combina modelo Flair com regras
    heurísticas específicas para o contexto de suporte técnico em português.
    """

    def __init__(self):
        """
        Inicializa o classificador carregando o modelo pré-treinado 'sentiment'
        do Flair e definindo os padrões semânticos usados nas heurísticas.
        """
        self.classifier = TextClassifier.load('sentiment')

        self.very_positive = [
            "extremamente satisfeito", "acima do esperado", "excelente",
            "ótimo", "muito bom", "impecável", "superou completamente",
            "nota 10", "melhor atendimento", "impressionada",
            "sem complicação", "prestativa", "recomendo",
            "muito bem preparados", "competentes", "eficiente", "rapidez",
            "primeira", "perfeito", "qualidade"
        ]

        self.very_negative = [
            "péssima", "decepcionante", "insatisfeito", "horrível",
            "inaceitável", "despreparo", "não resolveu",
            "não conseguiram resolver", "problema não foi resolvido",
            "desperdiçou", "perdi tempo", "não soube", "confuso",
            "contraditório", "ignorou", "fraco", "recorrente",
            "nunca resolvem", "total despreparo", "solução errada"
        ]

        self.neutral_indicators = [
            "mas", "porém", "contudo", "entretanto", "no entanto", "apesar de",
            "embora", "mesmo assim", "ainda assim", "por outro lado",
            "ao mesmo tempo", "educado mas", "respeitoso mas", "tentou mas",
            "esforço mas", "infelizmente não", "não era clara", "mediana",
            "poderia ser", "esperava mais", "não tão eficiente",
            "sem solução definitiva", "meio incompleta", "pela metade",
            "mais ou menos", "ok mas", "demorou um pouco", "não muito",
            "razoável", "aceitável"
        ]

        self.weakening_words = [
            "um pouco", "meio", "mais ou menos", "razoável", "aceitável", "ok",
            "regular", "satisfatório", "mediano", "comum", "normal", "padrão",
            "básico"
        ]

        self.negations = [
            "não", "nunca", "jamais", "nada", "nenhum", "nem", "tampouco",
            "sequer"
        ]

    def count_matches(self, text: str, patterns: List[str]) -> int:
        """
        Conta quantas expressões da lista aparecem no texto.

        Args:
            text (str): Texto a ser analisado.
            patterns (List[str]): Lista de padrões/palavras a serem procuradas.

        Returns:
            int: Quantidade de ocorrências encontradas no texto.
        """
        text_lower = text.lower()
        count = 0
        for pattern in patterns:
            if pattern.lower() in text_lower:
                count += 1
        return count

    def has_contradiction(self, text: str) -> bool:
        """
        Verifica se o texto possui expressões de contradição.

        Args:
            text (str): Texto a ser verificado.

        Returns:
            bool: True se houver contradição, False caso contrário.
        """
        contradiction_words = [
            "mas", "porém", "contudo", "entretanto", "no entanto", "apesar"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in contradiction_words)

    def analyze_sentiment_strength(self, text: str) -> Dict[str, float]:
        """
        Realiza a análise detalhada do sentimento do texto, combinando
        heurísticas e a predição do modelo Flair.

        Args:
            text (str): Texto da avaliação do cliente.

        Returns:
            Dict[str, float]: Dicionário com indicadores heurísticos e
            resultado do Flair.
        """
        very_pos_count = self.count_matches(text, self.very_positive)
        very_neg_count = self.count_matches(text, self.very_negative)
        neutral_count = self.count_matches(text, self.neutral_indicators)
        weakening_count = self.count_matches(text, self.weakening_words)
        has_contradiction = self.has_contradiction(text)

        sentence = Sentence(text)
        self.classifier.predict(sentence)
        flair_label = sentence.labels[0].value.lower()
        flair_confidence = sentence.labels[0].score

        return {
            'very_positive': very_pos_count,
            'very_negative': very_neg_count,
            'neutral_indicators': neutral_count,
            'weakening_words': weakening_count,
            'has_contradiction': has_contradiction,
            'flair_label': flair_label,
            'flair_confidence': flair_confidence
        }

    def classify_sentiment(self, text: str) -> str:
        """
        Classifica o sentimento do texto como positiva, neutra ou negativa.

        Args:
            text (str): Texto da avaliação do cliente.

        Returns:
            str: Classificação final do sentimento.
        """
        analysis = self.analyze_sentiment_strength(text)

        if analysis['neutral_indicators'] >= 2 or analysis['has_contradiction']:  # noqa: E501
            return "neutra"

        if analysis['weakening_words'] >= 2:
            return "neutra"

        if analysis['very_positive'] >= 1 and analysis['very_negative'] >= 1:
            return "neutra"

        if analysis['very_negative'] >= 2:
            return "negativa"

        if analysis['very_positive'] >= 2:
            return "positiva"

        if analysis['neutral_indicators'] >= 1 and analysis['flair_confidence'] < 0.8:  # noqa: E501
            return "neutra"

        if analysis['flair_confidence'] >= 0.9:
            return "positiva" if analysis['flair_label'] == "positive" else "negativa"  # noqa: E501

        if analysis['very_positive'] >= 1 and analysis['very_negative'] == 0:
            return "positiva"

        if analysis['very_negative'] >= 1 and analysis['very_positive'] == 0:
            return "negativa"

        if analysis['flair_confidence'] < 0.7:
            return "neutra"

        return "positiva" if analysis['flair_label'] == "positive" else "negativa"  # noqa: E501


# Instância global para uso na API
sentiment_classifier = SentimentClassifier()


def classify_sentiment(text: str) -> str:
    """
    Interface externa do classificador para uso na API.

    Args:
        text (str): Texto da avaliação a ser classificada.

    Returns:
        str: Resultado do sentimento classificado.
    """
    return sentiment_classifier.classify_sentiment(text)
