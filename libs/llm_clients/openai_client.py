import os
from typing import List, Dict, Any
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import openai

from .base import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text from a prompt."""
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages, **kwargs)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Chat with OpenAI using messages."""
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.dict(),
            finish_reason=response.choices[0].finish_reason,
        )
    
    async def summarize(self, text: str, **kwargs) -> LLMResponse:
        """Summarize the given text."""
        prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        return await self.generate_text(prompt, **kwargs)
    
    async def extract_keywords(self, text: str, **kwargs) -> List[str]:
        """Extract keywords from text."""
        prompt = f"""Extract the most important keywords and phrases from the following text. 
        Return them as a JSON list of strings.
        
        Text: {text}
        
        Keywords (JSON format):"""
        
        response = await self.generate_text(prompt, **kwargs)
        
        try:
            keywords = json.loads(response.content)
            return keywords if isinstance(keywords, list) else []
        except json.JSONDecodeError:
            # Fallback: split by commas and clean up
            return [k.strip() for k in response.content.split(",") if k.strip()]
    
    async def classify_text(self, text: str, categories: List[str], **kwargs) -> str:
        """Classify text into one of the given categories."""
        categories_str = ", ".join(categories)
        prompt = f"""Classify the following text into one of these categories: {categories_str}
        
        Text: {text}
        
        Category:"""
        
        response = await self.generate_text(prompt, **kwargs)
        
        # Find the best matching category
        content = response.content.strip().lower()
        for category in categories:
            if category.lower() in content:
                return category
        
        # Return first category as fallback
        return categories[0] if categories else "unknown"