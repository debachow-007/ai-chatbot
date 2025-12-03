import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db import SessionLocal, engine
from app.models import DocumentChunk
from app.services.embeddings import get_query_embedding
from app.db import Base

HARVESTED_PATH = Path("harvested/harvested_latest.jsonl")
CHUNK_SIZE = 800  # characters per chunk


def init_db():
    print("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("DB init complete")


def chunk_text(text: str, size: int = CHUNK_SIZE):
    lines = text.splitlines()
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > size:
            yield current
            current = ""
        current += ("\n" if current else "") + line
    if current:
        yield current


def ingest():
    if not HARVESTED_PATH.exists():
        raise FileNotFoundError(f"{HARVESTED_PATH} not found. Run crawler first.")

    print("Starting ingestion process")
    print(f"Reading file: {HARVESTED_PATH}")

    init_db()

    db: Session = SessionLocal()
    total_chunks = 0
    line_counter = 0

    with HARVESTED_PATH.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line_counter += 1
            row = json.loads(raw_line)

            url = row.get("url")
            title = row.get("title", "")
            content = row.get("content", "")

            print(f"\nProcessing page #{line_counter} | URL: {url}")

            chunk_list = list(chunk_text(content))
            print(f"Generated {len(chunk_list)} chunks")

            for idx, chunk in enumerate(chunk_list):
                print(f"Chunk {idx+1}/{len(chunk_list)} (len={len(chunk)})")

                try:
                    emb = get_query_embedding(chunk)
                    print("Embedding generated successfully")
                except Exception as e:
                    print(f"Embedding error: {e}")
                    continue

                try:
                    doc = DocumentChunk(
                        url=url,
                        title=title,
                        chunk_index=idx,
                        content=chunk,
                        embedding=emb,
                    )
                    db.add(doc)
                    total_chunks += 1
                except Exception as e:
                    print(f"Insert error: {e}")

    print("\nCommitting to database...")
    try:
        db.commit()
        print("Commit complete")
    except Exception as e:
        print(f"Commit failed: {e}")
        db.rollback()

    db.close()

    print(f"\nIngestion finished | Total pages: {line_counter} | Total chunks: {total_chunks}")


if __name__ == "__main__":
    ingest()
