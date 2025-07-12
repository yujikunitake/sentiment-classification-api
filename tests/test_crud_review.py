import pytest
from unittest.mock import MagicMock
from datetime import date

from app.schemas.review import ReviewBase, SentimentsEnum
from app.models.review import Review
import app.crud.review as crud


@pytest.fixture
def fake_review_data():
    """Retorna um ReviewBase válido para testes."""
    return ReviewBase(
        customer_name="Teste Cliente",
        review_text="Texto de teste para avaliação.",
        evaluation_date=date(2024, 8, 1),
    )


@pytest.fixture
def mock_db():
    """Retorna uma sessão de banco mockada com métodos básicos."""
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.query = MagicMock()
    return db


class TestCRUDReview:
    """Testes para as operações CRUD de avaliações."""

    def test_create_review_success(self, mock_db, fake_review_data):
        """Testa criação correta de avaliação com sentimento mockado."""
        crud.classify_sentiment = MagicMock(return_value=SentimentsEnum.POSITIVE.value)  # noqa: E501

        review = crud.create_review(mock_db, fake_review_data)

        crud.classify_sentiment.assert_called_once_with(fake_review_data.review_text)  # noqa: E501
        mock_db.add.assert_called_once_with(review)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(review)
        assert review.sentiment == SentimentsEnum.POSITIVE.value
        assert review.customer_name == fake_review_data.customer_name

    def test_create_review_invalid_sentiment_raises(self, mock_db, fake_review_data):  # noqa: E501
        """Testa erro ao classificar sentimento (simulado)."""
        crud.classify_sentiment = MagicMock(side_effect=ValueError("Erro na classificação"))  # noqa: E501

        with pytest.raises(ValueError):
            crud.create_review(mock_db, fake_review_data)

    def test_get_reviews_no_filters(self, mock_db):
        """Testa obtenção de todas avaliações sem filtro."""
        fake_reviews = [
            Review(
                id=1,
                customer_name="Cliente1",
                review_text="bom",
                evaluation_date=date(2024, 7, 1),
                sentiment=SentimentsEnum.POSITIVE.value,
            )
        ]
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value.all.return_value = fake_reviews
        mock_db.query.return_value = query_mock

        results = crud.get_reviews(mock_db)
        assert results == fake_reviews

    def test_get_reviews_with_filters(self, mock_db):
        """Testa obtenção de avaliações com filtro de datas."""
        fake_reviews = []
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value.all.return_value = fake_reviews
        mock_db.query.return_value = query_mock

        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        results = crud.get_reviews(mock_db, start_date=start, end_date=end)
        assert results == fake_reviews
        # Verifica se filtros foram aplicados
        assert query_mock.filter.call_count >= 2

    def test_get_review_by_id_found(self, mock_db):
        """Testa busca de avaliação existente por ID."""
        fake_review = Review(
            id=1,
            customer_name="Cliente1",
            review_text="bom",
            evaluation_date=date(2024, 7, 1),
            sentiment=SentimentsEnum.POSITIVE.value,
        )
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = fake_review
        mock_db.query.return_value = query_mock

        review = crud.get_review_by_id(mock_db, 1)
        assert review == fake_review

    def test_get_review_by_id_not_found(self, mock_db):
        """Testa busca de avaliação inexistente por ID."""
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        mock_db.query.return_value = query_mock

        review = crud.get_review_by_id(mock_db, 999)
        assert review is None

    def test_get_review_report(self, mock_db):
        """Testa geração do relatório de sentimentos."""
        results_from_db = [
            (SentimentsEnum.POSITIVE, 10),
            (SentimentsEnum.NEUTRAL, 5),
            (SentimentsEnum.NEGATIVE, 3),
        ]

        query_mock = MagicMock()
        query_mock.filter.return_value.group_by.return_value = results_from_db
        mock_db.query.return_value = query_mock

        report = crud.get_review_report(mock_db, date(2024, 1, 1), date(2024, 12, 31))  # noqa: E501

        expected = {
            SentimentsEnum.POSITIVE.value: 10,
            SentimentsEnum.NEUTRAL.value: 5,
            SentimentsEnum.NEGATIVE.value: 3,
        }
        assert report == expected

    def test_get_review_report_empty(self, mock_db):
        """Testa relatório vazio quando não há avaliações."""
        query_mock = MagicMock()
        query_mock.filter.return_value.group_by.return_value = []
        mock_db.query.return_value = query_mock

        report = crud.get_review_report(mock_db, date(2024, 1, 1), date(2024, 12, 31))  # noqa: E501
        expected = {
            SentimentsEnum.POSITIVE.value: 0,
            SentimentsEnum.NEUTRAL.value: 0,
            SentimentsEnum.NEGATIVE.value: 0,
        }
        assert report == expected
