from typing import List

import vertexai
from vertexai.preview import language_models  # or newer embedding API
from app.config import settings

vertexai.init(
    project=settings.PROJECT_ID,
    location=settings.LOCATION,
)


def get_query_embedding(text: str) -> List[float]:
    model = language_models.TextEmbeddingModel.from_pretrained(
        settings.EMBEDDING_MODEL
    )
    res = model.get_embeddings([text])
    return res[0].values
