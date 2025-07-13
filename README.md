# sentiment-classification-api
API RESTful desenvolvida com FastAPI para **classificar automaticamente sentimentos** de avaliações de clientes no contexto de **suporte técnico B2B** como **Positiva**, **Neutra** e **Negativa**.

## Principais tecnologias utilizadas:
- Python 3.12.7
- FastAPI
- Pydantic
- SQLAlchemy + PostgreSQL
- Flair + SpaCy + Heurísticas customizadas
- Pytest (com mocks)
- Dotenv

## Objetivo:
- Receber avaliações textuais de clientes;
- Classificar o sentimento (**positivo**, **neutro** ou **negativo**);
- Armazenar no banco de dados;
- Oferecer funcionalidades de consulta e relatório.

## Requisitos

- Python 3.12+
- PostgreSQL (rodando localmente ou em container)

## Como executar localmente:

### 1) Clone o repositório

```bash
git clone https://github.com/yujikunitake/sentiment-classification-api.git
cd sentiment-classification-api
```

### 2) Crie o ambiente virtual e ative

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows
```

### 3) Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Configure as variáveis de ambiente

Crie um arquivo .env com o seguinte conteúdo:
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/sentimentdb
```
Ajuste a URL conforme seu ambiente local.

### 5) Crie as tabelas no banco

```bash
python create_tables.py
```

### 6) Rode a aplicação

```bash
uvicorn app.main:app --reload
```

### 7) Acesse o Swagger

Acesse: http://127.0.0.1:8000/docs

## Endpoints disponíveis

| Método | Rota                 | Descrição                                               |
|--------|----------------------|----------------------------------------------------------|
| POST   | `/reviews/`          | Cria uma nova avaliação e classifica o sentimento       |
| GET    | `/reviews/`          | Lista todas as avaliações (com filtros por datas)       |
| GET    | `/reviews/{id}`      | Retorna uma avaliação específica pelo ID                |
| GET    | `/reviews/report`    | Retorna a contagem de sentimentos em um intervalo de datas |

## Modelo de classificação usado:

O projeto utiliza um modelo híbrido para análise de sentimentos, combinando **machine learning** com **regras heurísticas** personalizadas para o contexto de **suporte técnico B2B**.

### Modelo base

Foi utilizado o [Flair](https://github.com/flairNLP/flair), um framework de NLP baseado em PyTorch. O modelo carregado é:
```python
from flair.models import TextClassifier
classifier = TextClassifier.load("sentiment")
```
Esse modelo fornece uma classificação inicial com uma **pontuação de confiança**.

### Heurísticas complementares

Regras linguísticas foram adicionadas para melhor desempenho em casos ambíguos:

- Expressões muito positivas e muito negativas
- Indicadores de neutralidade (ex: “mas”, “porém”)
- Padrões contraditórios usando regex
- Lematização com `spaCy` (modelo pt_core_news_sm)

### Estratégia de decisão

A decisão final é feita ponderando:

- Palavras-chave positivas/negativas
- Termos neutros ou enfraquecedores
- Contradições linguísticas
- Confiança do modelo Flair

Toda a lógica está em `app/services/classifier.py`.

## Resultados

O classificador foi avaliado com mais de 35 exemplos reais e atingiu:

- Acurácia geral superior a 90%
- Acurácia por categoria acima de 80%

## Rodando os testes

### Testes Classificador:

```bash
pytest -s tests/test_classifier.py
```

### Testes CRUD:

```bash
pytest -s tests/test_crud_review.py
```

### Testes das rotas da API:

```bash
pytest -s tests/test_routes_review.py
```

## Exemplo de classificação

```json
{
  "customer_name": "João",
  "review_text": "O atendimento foi eficiente, mas poderia ser mais completo.",
  "evaluation_date": "2024-07-01"
}
```

Resultado:

```json
{
  "id": 1,
  "customer_name": "João",
  "review_text": "O atendimento foi eficiente, mas poderia ser mais completo.",
  "evaluation_date": "2024-07-01",
  "sentiment": "neutral"
}
```

## Links úteis

- [FastAPI](https://fastapi.tiangolo.com/)
- [Flair NLP](https://github.com/flairNLP/flair)
- [spaCy](https://spacy.io/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## Licença

MIT © 2025
