from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""
    content: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str
    metadata: Optional[Dict[str, Any]] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Chat with the LLM using messages."""
        pass
    
    @abstractmethod
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """Summarize the given text."""
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, **kwargs) -> List[str]:
        """Extract keywords from text."""
        pass
    
    @abstractmethod
    async def classify_text(self, text: str, categories: List[str], **kwargs) -> str:
        """Classify text into one of the given categories."""
        pass