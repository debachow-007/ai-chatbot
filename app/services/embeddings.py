from typing import List
import vertexai
from vertexai.language_models import TextEmbeddingModel
from app.config import settings

# Initialize Vertex client
vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)

# Load embedding model once globally
embedding_model = TextEmbeddingModel.from_pretrained(settings.EMBEDDING_MODEL)

def get_query_embedding(text: str) -> List[float]:
    response = embedding_model.get_embeddings([text])
    return response[0].values
