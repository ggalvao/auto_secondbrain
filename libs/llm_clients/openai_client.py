"""OpenAI client implementation."""

import json
import os
from typing import Any, Dict, List, Optional

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """OpenAI client for text generation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"
    ) -> None:
        """Initialize the OpenAI client."""
        self.api_key: Optional[str] = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model: str = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_text(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text from a prompt."""
        messages: List[Dict[str, str]] = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        """Chat with OpenAI using messages."""
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
        )

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage=response.usage.model_dump() if response.usage else {},
            finish_reason=response.choices[0].finish_reason or "",
        )

    async def summarize(self, text: str, **kwargs: Any) -> LLMResponse:
        """Summarize the given text."""
        prompt: str = (
            f"Please provide a concise summary of the following text:\n\n{text}"
        )
        return await self.generate_text(prompt, **kwargs)

    async def extract_keywords(self, text: str, **kwargs: Any) -> List[str]:
        """Extract keywords from text."""
        prompt: str = (
            "Extract the most important keywords and phrases from the following text.\n"
            "Return them as a JSON list of strings.\n\n"
            f"Text: {text}\n\n"
            "Keywords (JSON format):"
        )

        response = await self.generate_text(prompt, **kwargs)

        try:
            keywords: List[str] = json.loads(response.content)
            return keywords if isinstance(keywords, list) else []
        except json.JSONDecodeError:
            # Fallback: split by commas and clean up
            return [k.strip() for k in response.content.split(",") if k.strip()]

    async def classify_text(
        self, text: str, categories: List[str], **kwargs: Any
    ) -> str:
        """Classify text into one of the given categories."""
        categories_str: str = ", ".join(categories)
        prompt: str = (
            f"Classify the following text into one of these categories: "
            f"{categories_str}\n\n"
            f"Text: {text}\n\n"
            "Category:"
        )

        response = await self.generate_text(prompt, **kwargs)

        # Find the best matching category
        content: str = response.content.strip().lower()
        for category in categories:
            if category.lower() in content:
                return category

        # Return first category as fallback
        return categories[0] if categories else "unknown"
