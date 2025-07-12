from flair.models import TextClassifier
from flair.data import Sentence
from typing import Dict, List
from app.schemas.review import SentimentsEnum
import spacy
from unidecode import unidecode
import re


class SentimentClassifier:
    """
    Classificador de sentimentos com modelo Flair e heurísticas específicas
    para suporte técnico em português.
    """

    def __init__(self):
        self.classifier = TextClassifier.load('sentiment')
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
            "mas", "porém", "contudo", "entretanto", "no entanto", "apesar de",
            "embora", "mesmo assim", "ainda assim", "por outro lado",
            "ao mesmo tempo", "educado mas", "respeitoso mas", "tentou mas",
            "esforço mas", "infelizmente não", "não era clara", "mediana",
            "poderia ser", "esperava mais", "não tão eficiente",
            "agradeço pelo esforço", "sem solução definitiva",
            "meio incompleta", "pela metade", "mais ou menos", "ok mas",
            "demorou um pouco", "não muito", "razoável", "aceitável",
            "satisfatória", "poderia ser mais", "resultado final me deixou",
            "esperava mais", "espero que melhorem", "funcionado bem",
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

        # Padrões específicos para neutralidade
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
        text = unidecode(text.lower())
        doc = self.nlp(text)
        tokens = [
            token.lemma_ for token in doc
            if not token.is_stop and token.is_alpha
        ]
        return " ".join(tokens)

    def count_matches(self, text: str, patterns: List[str]) -> int:
        text = unidecode(text.lower())
        count = 0
        for pattern in patterns:
            pattern_norm = unidecode(pattern.lower())
            # Busca por palavras-chave principais do padrão
            if " " in pattern_norm:
                words = pattern_norm.split()
                # Verifica se todas as palavras principais estão presentes
                if all(word in text for word in words):
                    count += 1
            else:
                if pattern_norm in text:
                    count += 1
        return count

    def has_contradiction(self, original_text: str) -> bool:
        contradiction_words = [
            "mas", "porém", "contudo", "entretanto", "no entanto", "apesar"
        ]
        text = unidecode(original_text.lower())
        return any(word in text for word in contradiction_words)

    def matches_neutral_pattern(self, text: str) -> bool:
        """Verifica se o texto corresponde a padrões específicos de neutralidade"""
        text = unidecode(text.lower())
        for pattern in self.neutral_patterns:
            if re.search(pattern, text):
                return True
        return False

    def analyze_sentiment_strength(self, text: str) -> Dict[str, float]:
        processed_text = self.preprocess_text(text)
        original_text = text

        very_pos_count = self.count_matches(original_text, self.very_positive)
        very_neg_count = self.count_matches(original_text, self.very_negative)
        neutral_count = self.count_matches(original_text, self.neutral_indicators)
        weakening_count = self.count_matches(original_text, self.weakening_words)
        has_contradiction = self.has_contradiction(original_text)
        matches_neutral_pattern = self.matches_neutral_pattern(original_text)

        sentence = Sentence(original_text)
        self.classifier.predict(sentence)
        flair_label = sentence.labels[0].value.lower()
        flair_confidence = sentence.labels[0].score

        return {
            'very_positive': very_pos_count,
            'very_negative': very_neg_count,
            'neutral_indicators': neutral_count,
            'weakening_words': weakening_count,
            'has_contradiction': has_contradiction,
            'matches_neutral_pattern': matches_neutral_pattern,
            'flair_label': flair_label,
            'flair_confidence': flair_confidence
        }

    def classify_sentiment(self, text: str) -> str:
        analysis = self.analyze_sentiment_strength(text)

        # PRIORIDADE MÁXIMA: Padrões específicos de neutralidade
        if analysis['matches_neutral_pattern']:
            return SentimentsEnum.NEUTRAL.value

        # PRIORIDADE ALTA: negatividade evidente
        if analysis['very_negative'] >= 3:
            return SentimentsEnum.NEGATIVE.value

        # Neutro forte por ambivalência clara
        if analysis['neutral_indicators'] >= 3 or (analysis['has_contradiction'] and analysis['neutral_indicators'] >= 2):
            return SentimentsEnum.NEUTRAL.value

        # Neutro por conteúdo claramente misto
        if analysis['very_positive'] >= 2 and analysis['very_negative'] >= 1:
            return SentimentsEnum.NEUTRAL.value

        # Neutro por palavras enfraquecedoras em contexto ambíguo
        if analysis['weakening_words'] >= 2 and analysis['has_contradiction']:
            return SentimentsEnum.NEUTRAL.value

        # Regras de polaridade explícita forte
        if analysis['very_negative'] >= 2 and analysis['very_positive'] == 0:
            return SentimentsEnum.NEGATIVE.value

        if analysis['very_positive'] >= 3:
            return SentimentsEnum.POSITIVE.value

        # Neutro se há contradição com baixa confiança do modelo
        if analysis['has_contradiction'] and analysis['flair_confidence'] < 0.8:
            return SentimentsEnum.NEUTRAL.value

        # Alta confiança do modelo sem contradições
        if analysis['flair_confidence'] >= 0.9 and not analysis['has_contradiction']:
            return (
                SentimentsEnum.POSITIVE.value
                if analysis['flair_label'] == "positive"
                else SentimentsEnum.NEGATIVE.value
            )

        # Heurísticas claras sem ambiguidade
        if analysis['very_positive'] >= 2 and analysis['very_negative'] == 0 and not analysis['has_contradiction']:
            return SentimentsEnum.POSITIVE.value

        if analysis['very_negative'] >= 1 and analysis['very_positive'] == 0 and not analysis['has_contradiction']:
            return SentimentsEnum.NEGATIVE.value

        # Positivo claro com uma palavra muito positiva e alta confiança
        if analysis['very_positive'] >= 1 and analysis['very_negative'] == 0 and analysis['flair_confidence'] >= 0.85 and not analysis['has_contradiction']:
            return SentimentsEnum.POSITIVE.value

        # Baixa confiança ou ambiguidade => neutro
        if analysis['flair_confidence'] < 0.7 or analysis['has_contradiction']:
            return SentimentsEnum.NEUTRAL.value

        # fallback com o modelo Flair
        return (
            SentimentsEnum.POSITIVE.value
            if analysis['flair_label'] == "positive"
            else SentimentsEnum.NEGATIVE.value
        )


# Instância global
sentiment_classifier = SentimentClassifier()


def classify_sentiment(text: str) -> str:
    return sentiment_classifier.classify_sentiment(text)