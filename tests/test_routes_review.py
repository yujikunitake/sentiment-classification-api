"""Testes das rotas da API de avaliações."""

from datetime import date
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def fake_review():
    """Retorna um dicionário representando uma avaliação simulada."""
    return {
        "customer_name": "Cliente Teste",
        "review_text": "Excelente suporte técnico!",
        "evaluation_date": "2024-07-01"
    }


def test_create_review_success(fake_review):
    """
    Testa a criação de uma nova avaliação com sucesso.

    Args:
        fake_review (dict): Dados simulados da avaliação.

    Asserts:
        O status code da resposta é 201.
        O corpo da resposta contém os dados esperados.
    """
    with patch("app.routers.review.classify_sentiment", return_value="positive"), patch("app.routers.review.create_review") as mock_create:  # noqa: E501
        mock_create.return_value = MagicMock(
            id=1,
            customer_name=fake_review["customer_name"],
            review_text=fake_review["review_text"],
            evaluation_date=date.fromisoformat(fake_review["evaluation_date"]),
            sentiment="positive"
        )

        response = client.post("/reviews/", json=fake_review)

        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == fake_review["customer_name"]
        assert data["review_text"] == fake_review["review_text"]
        assert data["sentiment"] == "positive"
        assert "id" in data


def test_list_reviews_success():
    """
    Testa a listagem de avaliações sem filtros.

    Asserts:
        O status da resposta é 200.
        A resposta contém uma lista de avaliações.
    """
    with patch("app.routers.review.get_reviews") as mock_list:
        mock_list.return_value = [
            MagicMock(
                id=1,
                customer_name="Cliente A",
                review_text="Muito bom",
                evaluation_date=date(2024, 7, 1),
                sentiment="positive"
            )
        ]

        response = client.get("/reviews/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["sentiment"] == "positive"


def test_get_review_by_id_found():
    """
    Testa a recuperação de uma avaliação existente por ID.

    Asserts:
        O status é 200.
        O corpo da resposta contém a avaliação esperada.
    """
    with patch("app.routers.review.get_review_by_id") as mock_get:
        mock_get.return_value = MagicMock(
            id=1,
            customer_name="Cliente Teste",
            review_text="Texto",
            evaluation_date=date(2024, 7, 1),
            sentiment="neutral"
        )

        response = client.get("/reviews/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["sentiment"] == "neutral"


def test_get_review_by_id_not_found():
    """
    Testa o retorno 404 quando a avaliação não é encontrada.

    Asserts:
        O status da resposta é 404.
        A mensagem de erro é adequada.
    """
    with patch("app.routers.review.get_review_by_id", return_value=None):
        response = client.get("/reviews/999")

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]


def test_get_review_report():
    """
    Testa a geração de relatório de sentimentos.

    Asserts:
        O status é 200.
        A resposta contém os totais por tipo de sentimento.
    """
    with patch("app.routers.review.get_review_report") as mock_report:
        mock_report.return_value = {
            "positive": 10,
            "neutral": 5,
            "negative": 3
        }

        response = client.get("/reviews/report?start_date=2024-07-01&end_date=2024-07-31")  # noqa: E501

        assert response.status_code == 200
        data = response.json()
        assert data["positive"] == 10
        assert data["neutral"] == 5
        assert data["negative"] == 3
