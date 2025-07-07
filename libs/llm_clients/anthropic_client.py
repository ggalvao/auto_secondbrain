# mypy: ignore-file

import os
from typing import List, Dict, Any, Optional
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import anthropic

from .base import LLMClient, LLMResponse


class AnthropicClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model: str = model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

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
        """Chat with Anthropic using messages."""
        response = await self.client.messages.create(
            model=kwargs.get("model", self.model),
            messages=messages,  # type: ignore
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
        )

        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "",
        )

    async def summarize(self, text: str, **kwargs: Any) -> LLMResponse:
        """Summarize the given text."""
        prompt: str = (
            f"Please provide a concise summary of the following text:\n\n{text}"
        )
        return await self.generate_text(prompt, **kwargs)

    async def extract_keywords(self, text: str, **kwargs: Any) -> List[str]:
        """Extract keywords from text."""
        prompt: str = f"""Extract the most important keywords and phrases from the following text. 
        Return them as a JSON list of strings.
        
        Text: {text}
        
        Keywords (JSON format):"""

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
        prompt: str = f"""Classify the following text into one of these categories: {categories_str}
        
        Text: {text}
        
        Category:"""

        response = await self.generate_text(prompt, **kwargs)

        # Find the best matching category
        content: str = response.content.strip().lower()
        for category in categories:
            if category.lower() in content:
                return category

        # Return first category as fallback
        return categories[0] if categories else "unknown"
