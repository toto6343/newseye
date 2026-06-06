import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        
        if settings.OPENAI_API_KEY:
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name="text-embedding-3-small"
            )
        else:
            logger.warning("OPENAI_API_KEY not found. Using default embedding function (SentencesTransformer).")
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name="security_news",
            embedding_function=self.embedding_fn
        )

    async def add_news(self, news_id: int, title: str, content: str, metadata: Dict[str, Any]):
        """Adds or updates a news article in the vector store."""
        try:
            self.collection.upsert(
                ids=[str(news_id)],
                documents=[f"Title: {title}\n\nContent: {content}"],
                metadatas=[metadata]
            )
        except Exception as e:
            logger.error(f"Error adding news to vector store: {e}")

    async def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Queries the vector store for relevant documents."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

rag_service = RAGService()
