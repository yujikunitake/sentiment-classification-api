"""Operações CRUD para o modelo Review."""

from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.review import Review
from app.schemas.review import ReviewBase, SentimentsEnum
from app.services.classifier import classify_sentiment


def create_review(db: Session, review_data: ReviewBase) -> Review:
    """Cria uma nova avaliação no banco de dados após classificar o sentimento.

    Args:
        db (Session): Sessão ativa do banco de dados.
        review_data (ReviewBase): Dados da avaliação fornecida pelo cliente.

    Returns:
        Review: Objeto da avaliação criada.
    """
    sentiment = classify_sentiment(review_data.review_text)

    review = Review(
        customer_name=review_data.customer_name,
        review_text=review_data.review_text,
        evaluation_date=review_data.evaluation_date,
        sentiment=sentiment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Review]:
    """Retorna todas as avaliações, com filtro opcional por intervalo de datas.

    Args:
        db (Session): Sessão ativa do banco de dados.
        start_date (Optional[date]): Data inicial do filtro.
        end_date (Optional[date]): Data final do filtro.

    Returns:
        List[Review]: Lista de avaliações encontradas.
    """
    query = db.query(Review)
    if start_date:
        query = query.filter(Review.evaluation_date >= start_date)
    if end_date:
        query = query.filter(Review.evaluation_date <= end_date)
    return query.order_by(Review.evaluation_date.desc()).all()


def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
    """Busca uma avaliação específica pelo ID.

    Args:
        db (Session): Sessão ativa do banco de dados.
        review_id (int): ID da avaliação desejada.

    Returns:
        Optional[Review]: Objeto da avaliação se encontrada, senão None.
    """
    return db.query(Review).filter(Review.id == review_id).first()


def get_review_report(db: Session, start_date: date, end_date: date) -> Dict[str, int]:  # noqa:E501
    """Gera um relatório com contagem de sentimentos em um intervalo de datas.

    Args:
        db (Session): Sessão ativa do banco de dados.
        start_date (date): Data inicial do período.
        end_date (date): Data final do período.

    Returns:
        Dict[str, int]: Dict com chaves "positive", "neutral" e "negative".
    """
    query = (
        db.query(Review.sentiment, func.count(Review.id))
        .filter(
            and_(
                Review.evaluation_date >= start_date,
                Review.evaluation_date <= end_date,
            )
        )
        .group_by(Review.sentiment)
    )

    results = {sentiment.value: 0 for sentiment in SentimentsEnum}
    for sentiment, count in query:
        results[sentiment.value] = count
    return results
