"""Rotas para criação, listagem e consulta de avaliações."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.classifier import classify_sentiment
from app.crud.review import (
    create_review,
    get_reviews,
    get_review_report,
    get_review_by_id,
)

review_router = APIRouter()


@review_router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Cria uma nova avaliação com classificação automática de sentimento."""
    try:
        sentiment = classify_sentiment(review_in.review_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao classificar sentimento: {str(e)}",
        )

    review = Review(
        customer_name=review_in.customer_name,
        review_text=review_in.review_text,
        evaluation_date=review_in.evaluation_date,
        sentiment=sentiment,
    )

    try:
        review = create_review(db, review)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar review no banco de dados: {str(e)}",
        )

    return review


@review_router.get("/", response_model=List[ReviewResponse])
def list_reviews(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
) -> List[ReviewResponse]:
    """Lista avaliações com filtro opcional por intervalo de datas."""
    try:
        return get_reviews(db, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar reviews: {str(e)}",
        )


@review_router.get("/report")
def get_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
):
    """Gera relatório de avaliações por tipo de sentimento."""
    try:
        return get_review_report(db, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}",
        )


@review_router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Recupera uma avaliação específica pelo ID."""
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review não encontrado")
    return review
