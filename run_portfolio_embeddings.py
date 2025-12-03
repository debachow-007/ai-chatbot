from app.db import SessionLocal
from app.models import PortfolioItem
from app.services.embeddings import get_query_embedding

db = SessionLocal()
items = db.query(PortfolioItem).all()

for item in items:
    if item.embedding is None:
        print(f"Embedding for: {item.title}")
        emb = get_query_embedding(f"{item.title} {item.description}")
        item.embedding = emb
        db.add(item)

db.commit()
db.close()
print("Portfolio embeddings saved.")
