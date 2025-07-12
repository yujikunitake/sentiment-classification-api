from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.schemas.review import (
    ReviewCreate,
    ReviewResponse
)
from app.database import get_db
from app.services.classifier import classify_sentiment
from app.crud.review import (
    create_review,
    get_reviews,
    get_review_report,
    get_review_by_id
)
from app.models.review import Review

review_router = APIRouter()


@review_router.post(
        "/",
        response_model=ReviewResponse,
        status_code=status.HTTP_201_CREATED
)
def post_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db)
) -> ReviewResponse:
    """
    Cria uma nova avaliação de cliente com classificação de sentimento
    automática.

    Args:
        review_in (ReviewCreate): Dados da avaliação recebida via POST.
        db (Session): Sessão do banco de dados injetada pelo FastAPI.

    Returns:
        ReviewResponse: Dados da avaliação salva com sentimento classificado.

    Raises:
        HTTPException: Se houver erro na classificação ou ao salvar no banco.
    """
    try:
        sentiment = classify_sentiment(review_in.review_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao classificar sentimento: {str(e)}"
        )

    review = Review(
        customer_name=review_in.customer_name,
        review_text=review_in.review_text,
        evaluation_date=review_in.evaluation_date,
        sentiment=sentiment
    )

    try:
        review = create_review(db, review)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar review no banco de dados: {str(e)}"
        )

    return review


@review_router.get("/", response_model=List[ReviewResponse])
def list_reviews(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
) -> List[ReviewResponse]:
    """
    Lista avaliações de clientes com filtro opcional por intervalo de datas.

    Args:
        start_date (Optional[date]): Data inicial para filtrar as avaliações.
        end_date (Optional[date]): Data final para filtrar as avaliações.
        db (Session): Sessão do banco de dados.

    Returns:
        List[ReviewResponse]: Lista de avaliações filtradas.

    Raises:
        HTTPException: Em caso de erro ao consultar o banco.
    """
    try:
        return get_reviews(db, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar reviews: {str(e)}"
        )


@review_router.get("/report")
def get_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Gera relatório de quantidade de avaliações por tipo de sentimento.

    Args:
        start_date (date): Data inicial do período a ser analisado.
        end_date (date): Data final do período a ser analisado.
        db (Session): Sessão do banco de dados.

    Returns:
        dict: Quantidade de avaliações por sentimento (positivo, neutro,
        negativo).

    Raises:
        HTTPException: Em caso de erro na consulta.
    """
    try:
        return get_review_report(db, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@review_router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
) -> ReviewResponse:
    """
    Recupera uma avaliação específica a partir do ID fornecido.

    Args:
        review_id (int): Identificador único da avaliação.
        db (Session): Sessão do banco de dados.

    Returns:
        ReviewResponse: Dados completos da avaliação localizada.

    Raises:
        HTTPException: Se a avaliação não for encontrada.
    """
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review não encontrado")
    return review
