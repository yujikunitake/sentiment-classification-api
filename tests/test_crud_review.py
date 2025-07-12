import pytest
from unittest.mock import MagicMock
from datetime import date

from app.schemas.review import ReviewBase, SentimentsEnum
from app.models.review import Review
import app.crud.review as crud


@pytest.fixture
def fake_review_data():
    return ReviewBase(
        customer_name="Teste Cliente",
        review_text="Texto de teste para avaliação.",
        evaluation_date=date(2024, 8, 1)
    )


def test_create_review(fake_review_data):
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()

    # Mockar classify_sentiment para retornar um sentimento fixo
    crud.classify_sentiment = MagicMock(
        return_value=SentimentsEnum.POSITIVE.value
    )

    review = crud.create_review(db, fake_review_data)

    # Validar se a função classify_sentiment foi chamada
    crud.classify_sentiment.assert_called_once_with(
        fake_review_data.review_text
    )

    # Verifica se os métodos do db foram chamados
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(review)

    # Verifica se o objeto retornado tem o sentimento mockado
    assert review.sentiment == SentimentsEnum.POSITIVE.value
    assert review.customer_name == fake_review_data.customer_name
    assert review.review_text == fake_review_data.review_text
    assert review.evaluation_date == fake_review_data.evaluation_date


def test_get_reviews():
    db = MagicMock()

    # Simula query retornando uma lista de Reviews
    fake_reviews = [
        Review(
            id=1,
            customer_name="Cliente1",
            review_text="bom",
            evaluation_date=date(2024, 7, 1),
            sentiment=SentimentsEnum.POSITIVE.value
        ),
        Review(
            id=2,
            customer_name="Cliente2",
            review_text="ruim",
            evaluation_date=date(2024, 7, 2),
            sentiment=SentimentsEnum.NEGATIVE.value
        ),
    ]

    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value.all.return_value = fake_reviews
    db.query.return_value = query_mock

    # Testa filtro sem datas
    results = crud.get_reviews(db)
    assert results == fake_reviews

    # Testa filtro com start_date
    results = crud.get_reviews(db, start_date=date(2024, 7, 1))
    assert db.query.call_count >= 1
    query_mock.filter.assert_called()

    # Testa filtro com end_date
    results = crud.get_reviews(db, end_date=date(2024, 7, 2))
    assert results == fake_reviews


def test_get_review_by_id():
    db = MagicMock()
    fake_review = Review(
        id=1,
        customer_name="Cliente1",
        review_text="bom",
        evaluation_date=date(2024, 7, 1),
        sentiment=SentimentsEnum.POSITIVE.value
    )
    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = fake_review
    db.query.return_value = query_mock

    review = crud.get_review_by_id(db, review_id=1)
    db.query.assert_called_once()
    query_mock.filter.assert_called_once()
    assert review == fake_review


def test_get_review_report():
    db = MagicMock()

    # Simula resultados de consulta
    results_from_db = [
        (SentimentsEnum.POSITIVE, 5),
        (SentimentsEnum.NEUTRAL, 3),
        (SentimentsEnum.NEGATIVE, 2),
    ]

    query_mock = MagicMock()
    query_mock.filter.return_value.group_by.return_value = results_from_db
    db.query.return_value = query_mock

    report = crud.get_review_report(
        db,
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 31)
    )

    assert report == {
        SentimentsEnum.POSITIVE.value: 5,
        SentimentsEnum.NEUTRAL.value: 3,
        SentimentsEnum.NEGATIVE.value: 2
    }
