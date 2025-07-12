"""Módulo para classificação de sentimentos com modelo Flair e heurísticas."""

import re
from typing import Dict, List

import spacy
from flair.data import Sentence
from flair.models import TextClassifier
from unidecode import unidecode

from app.schemas.review import SentimentsEnum


class SentimentClassifier:
    """Classificador de sentimentos com regras específicas para suporte B2B."""

    def __init__(self):
        self.classifier = TextClassifier.load("sentiment")
        self.nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])

        self.very_positive = [
            "extremamente satisfeito", "acima do esperado", "excelente",
            "ótimo", "muito bom", "impecável", "superou completamente",
            "nota 10", "melhor atendimento", "impressionada", "adorei",
            "sem complicação", "prestativa", "recomendo", "surpreendeu",
            "muito bem preparados", "competentes", "eficiente", "rapidez",
            "primeira", "perfeito", "qualidade", "atenciosa", "dedicada",
            "prático", "sem nenhuma complicação", "realmente de qualidade",
            "muito prestativa", "se dedicou", "superou", "expectativas"
        ]

        self.very_negative = [
            "péssima", "decepcionante", "insatisfeito", "horrível",
            "inaceitável", "despreparo", "não resolveu", "despreparado",
            "não conseguiram resolver", "problema não foi resolvido",
            "desperdiçou", "perdi tempo", "não soube", "confuso",
            "contraditório", "ignorou", "fraco", "recorrente", "demorado",
            "nunca resolvem", "total despreparo", "solução errada",
            "muito tempo", "não tive uma boa experiência", "frustrado",
            "vou reconsiderar", "bastante insatisfeito", "decepcionado",
            "completamente despreparado", "não conseguiu solucionar",
            "falta de consistência", "muito mais tempo", "não era clara"
        ]

        self.neutral_indicators = [
            "mas", "porém", "contudo", "entretanto", "no entanto",
            "apesar de", "embora", "mesmo assim", "ainda assim",
            "por outro lado", "ao mesmo tempo", "educado mas",
            "respeitoso mas", "tentou mas", "esforço mas",
            "infelizmente não", "não era clara", "mediana", "poderia ser",
            "esperava mais", "não tão eficiente", "agradeço pelo esforço",
            "sem solução definitiva", "meio incompleta", "pela metade",
            "mais ou menos", "ok mas", "demorou um pouco", "não muito",
            "razoável", "aceitável", "satisfatória", "poderia ser mais",
            "resultado final me deixou", "esperava mais",
            "espero que melhorem", "funcionado bem",
            "não conseguiu solucionar", "tentou várias", "ao final",
            "agradeço pelo esforço", "infelizmente não conseguiu"
        ]

        self.weakening_words = [
            "um pouco", "meio", "mais ou menos", "razoável", "aceitável", "ok",
            "regular", "satisfatório", "mediano", "comum", "normal", "padrão",
            "básico", "no geral"
        ]

        self.negations = [
            "não", "nunca", "jamais", "nada", "nenhum", "nem", "tampouco",
            "sequer", "infelizmente"
        ]

        self.neutral_patterns = [
            r"educado.*mas.*não conseguiu",
            r"respeitoso.*mas.*infelizmente",
            r"tentou.*mas.*não.*solução",
            r"esforço.*mas.*resultado.*frustrado",
            r"funcionado bem.*mas.*não.*eficiente",
            r"poderia ser.*mais.*detalhado",
            r"satisfatória.*mas.*poderia.*completa"
        ]

    def preprocess_text(self, text: str) -> str:
        """Pré-processa o texto aplicando normalização e lematização."""
        text = unidecode(text.lower())
        doc = self.nlp(text)
        tokens = [
            token.lemma_ for token in doc
            if not token.is_stop and token.is_alpha
        ]
        return " ".join(tokens)

    def count_matches(self, text: str, patterns: List[str]) -> int:
        """Conta quantas expressões da lista estão presentes no texto."""
        text = unidecode(text.lower())
        count = 0
        for pattern in patterns:
            words = unidecode(pattern.lower()).split()
            if all(word in text for word in words):
                count += 1
        return count

    def has_contradiction(self, text: str) -> bool:
        """Verifica se há palavras de contradição no texto."""
        contradiction_words = [
            "mas", "porém", "contudo", "entretanto", "no entanto", "apesar"
        ]
        text = unidecode(text.lower())
        return any(word in text for word in contradiction_words)

    def matches_neutral_pattern(self, text: str) -> bool:
        """Verifica se o texto corresponde a padrões específicos de
        neutralidade."""
        text = unidecode(text.lower())
        return any(re.search(pattern, text) for pattern in self.neutral_patterns)  # noqa: E501

    def analyze_sentiment_strength(self, text: str) -> Dict[str, float]:
        """Executa todas as análises heurísticas e de modelo sobre o texto."""
        very_pos = self.count_matches(text, self.very_positive)
        very_neg = self.count_matches(text, self.very_negative)
        neutral = self.count_matches(text, self.neutral_indicators)
        weak = self.count_matches(text, self.weakening_words)
        has_contra = self.has_contradiction(text)
        is_neutral_pattern = self.matches_neutral_pattern(text)

        sentence = Sentence(text)
        self.classifier.predict(sentence)
        flair_label = sentence.labels[0].value.lower()
        flair_conf = sentence.labels[0].score

        return {
            "very_positive": very_pos,
            "very_negative": very_neg,
            "neutral_indicators": neutral,
            "weakening_words": weak,
            "has_contradiction": has_contra,
            "matches_neutral_pattern": is_neutral_pattern,
            "flair_label": flair_label,
            "flair_confidence": flair_conf,
        }

    def classify_sentiment(self, text: str) -> str:
        """Classifica o sentimento com base em heurísticas e modelo."""
        a = self.analyze_sentiment_strength(text)

        if a["matches_neutral_pattern"]:
            return SentimentsEnum.NEUTRAL.value

        if a["very_negative"] >= 3:
            return SentimentsEnum.NEGATIVE.value

        if a["neutral_indicators"] >= 3 or (
            a["has_contradiction"] and a["neutral_indicators"] >= 2
        ):
            return SentimentsEnum.NEUTRAL.value

        if a["very_positive"] >= 2 and a["very_negative"] >= 1:
            return SentimentsEnum.NEUTRAL.value

        if a["weakening_words"] >= 2 and a["has_contradiction"]:
            return SentimentsEnum.NEUTRAL.value

        if a["very_negative"] >= 2 and a["very_positive"] == 0:
            return SentimentsEnum.NEGATIVE.value

        if a["very_positive"] >= 3:
            return SentimentsEnum.POSITIVE.value

        if a["has_contradiction"] and a["flair_confidence"] < 0.8:
            return SentimentsEnum.NEUTRAL.value

        if a["flair_confidence"] >= 0.9 and not a["has_contradiction"]:
            return (
                SentimentsEnum.POSITIVE.value
                if a["flair_label"] == "positive"
                else SentimentsEnum.NEGATIVE.value
            )

        if a["very_positive"] >= 2 and a["very_negative"] == 0 and not a["has_contradiction"]:  # noqa: E501
            return SentimentsEnum.POSITIVE.value

        if a["very_negative"] >= 1 and a["very_positive"] == 0 and not a["has_contradiction"]:  # noqa: E501
            return SentimentsEnum.NEGATIVE.value

        if (
            a["very_positive"] >= 1 and
            a["very_negative"] == 0 and
            a["flair_confidence"] >= 0.85 and
            not a["has_contradiction"]
        ):
            return SentimentsEnum.POSITIVE.value

        if a["flair_confidence"] < 0.7 or a["has_contradiction"]:
            return SentimentsEnum.NEUTRAL.value

        return (
            SentimentsEnum.POSITIVE.value
            if a["flair_label"] == "positive"
            else SentimentsEnum.NEGATIVE.value
        )


# Instância global
sentiment_classifier = SentimentClassifier()


def classify_sentiment(text: str) -> str:
    """Função auxiliar que delega ao classificador global."""
    return sentiment_classifier.classify_sentiment(text)
