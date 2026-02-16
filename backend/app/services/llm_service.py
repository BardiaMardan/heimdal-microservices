import google.generativeai as genai
from typing import AsyncGenerator
import os
from app.core.config import settings

class LLMService:
    def __init__(self):
        self._configured = False
        self._model = None

    def _configure(self):
        if self._configured:
            return
        
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            return

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-flash-latest")
        self._configured = True

    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        if not self._configured:
            self._configure()
        
        if not self._model:
            yield "LLM Service not configured. Please check GOOGLE_AI_API_KEY."
            return

        # TODO: manage history here
        response = await self._model.generate_content_async(message, stream=True)
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text

llm_service = LLMService()
