from typing import List, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

from .base import VectorDatabase, Document, SearchResult


class InMemoryVectorDB(VectorDatabase):
    """In-memory vector database implementation for development."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

    async def add_document(self, document: Document) -> str:
        """Add a document to the database."""
        if document.embedding is None:
            document.embedding = await self.get_embedding(document.content)

        self.documents[document.id] = document
        self.embeddings[document.id] = document.embedding

        return document.id

    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add multiple documents to the database."""
        ids = []
        for doc in documents:
            doc_id = await self.add_document(doc)
            ids.append(doc_id)
        return ids

    async def search(
        self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents."""
        query_embedding = await self.get_embedding(query)
        return await self.search_by_embedding(query_embedding, top_k, filters)

    async def search_by_embedding(
        self,
        embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search using embedding vector."""
        if not self.embeddings:
            return []

        # Calculate similarities
        similarities = []
        for doc_id, doc_embedding in self.embeddings.items():
            doc = self.documents[doc_id]

            # Apply filters if provided
            if filters:
                skip = False
                for key, value in filters.items():
                    if key not in doc.metadata or doc.metadata[key] != value:
                        skip = True
                        break
                if skip:
                    continue

            # Calculate cosine similarity
            similarity = np.dot(embedding, doc_embedding) / (
                np.linalg.norm(embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((doc_id, similarity))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = []

        for rank, (doc_id, score) in enumerate(similarities[:top_k]):
            results.append(
                SearchResult(
                    document=self.documents[doc_id], score=score, rank=rank + 1
                )
            )

        return results

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(document_id)

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID."""
        if document_id in self.documents:
            del self.documents[document_id]
            del self.embeddings[document_id]
            return True
        return False

    async def update_document(self, document_id: str, document: Document) -> bool:
        """Update a document."""
        if document_id not in self.documents:
            return False

        if document.embedding is None:
            document.embedding = await self.get_embedding(document.content)

        self.documents[document_id] = document
        self.embeddings[document_id] = document.embedding

        return True

    async def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        return self.model.encode(text)
