from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class Document:
    """Represents a document with embeddings."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class SearchResult:
    """Represents a search result."""
    document: Document
    score: float
    rank: int


class VectorDatabase(ABC):
    """Abstract base class for vector databases."""
    
    @abstractmethod
    async def add_document(self, document: Document) -> str:
        """Add a document to the database."""
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add multiple documents to the database."""
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 10, 
                    filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def search_by_embedding(self, embedding: np.ndarray, top_k: int = 10,
                                 filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search using embedding vector."""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID."""
        pass
    
    @abstractmethod
    async def update_document(self, document_id: str, document: Document) -> bool:
        """Update a document."""
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        pass