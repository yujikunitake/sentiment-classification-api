from fastapi import FastAPI
from app.routers.review import review_router

app = FastAPI(title="Sentiment Reviews API")

app.include_router(review_router, prefix="/reviews", tags=["reviews"])
