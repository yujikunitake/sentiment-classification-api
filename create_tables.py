from app.database import Base, engine
# Import abaixo é necessário p/ registrar o  modelo
from app.models.review import Review  # noqa: F401

Base.metadata.create_all(bind=engine)
