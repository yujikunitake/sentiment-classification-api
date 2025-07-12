"""Rotas RESTful para criação, listagem e consulta de avaliações."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
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

review_router = APIRouter(prefix="/reviews", tags=["Avaliações"])


@review_router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova avaliação",
    response_description="Avaliação criada com sucesso",
)
def create_new_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Cria uma nova avaliação com classificação automática de sentimento."""
    try:
        sentiment = classify_sentiment(review_in.review_text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Texto da avaliação inválido para classificação: "
                f"{str(e)}"
            ),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao classificar o sentimento.",
        )

    review = Review(
        customer_name=review_in.customer_name,
        review_text=review_in.review_text,
        evaluation_date=review_in.evaluation_date,
        sentiment=sentiment,
    )

    try:
        return create_review(db, review)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar a avaliação no banco de dados.",
        )


@review_router.get(
    "/",
    response_model=List[ReviewResponse],
    summary="Listar avaliações",
    response_description="Lista de avaliações encontradas",
)
def list_reviews(
    start_date: Optional[date] = Query(
        None, description="Data inicial (yyyy-mm-dd)"
    ),
    end_date: Optional[date] = Query(
        None, description="Data final (yyyy-mm-dd)"
    ),
    db: Session = Depends(get_db),
) -> List[ReviewResponse]:
    """Lista avaliações com filtro opcional por intervalo de datas."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data inicial não pode ser posterior à data final.",
        )

    try:
        return get_reviews(db, start_date, end_date)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao recuperar avaliações.",
        )


@review_router.get(
    "/report",
    summary="Relatório de sentimentos",
    response_description="Distribuição de sentimentos entre as avaliações",
)
def get_report(
    start_date: date = Query(..., description="Data inicial (yyyy-mm-dd)"),
    end_date: date = Query(..., description="Data final (yyyy-mm-dd)"),
    db: Session = Depends(get_db),
):
    """Gera relatório de avaliações por tipo de sentimento."""
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data inicial não pode ser posterior à data final.",
        )

    try:
        return get_review_report(db, start_date, end_date)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar relatório de sentimentos.",
        )


@review_router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Obter avaliação por ID",
    response_description="Avaliação encontrada",
)
def get_review_by_id_route(
    review_id: int,
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """Recupera uma avaliação específica pelo ID."""
    try:
        review = get_review_by_id(db, review_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar a avaliação no banco de dados.",
        )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avaliação com ID {review_id} não encontrada.",
        )

    return review
