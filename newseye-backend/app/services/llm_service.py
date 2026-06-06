import asyncio
import logging
from typing import List, Dict
import json
import httpx
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.use_local = settings.USE_LOCAL_LLM
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.ollama_model = settings.OLLAMA_MODEL
        
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key and not self.use_local:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            if not self.use_local:
                logger.warning("OPENAI_API_KEY not found. Defaulting to local LLM (Ollama).")
                self.use_local = True
            self.client = None

    async def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Helper method to call local Ollama instance"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.ollama_model,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise e

    async def analyze_article(self, content: str) -> dict:
        """
        Calls API (OpenAI or Local Ollama) to analyze article with MITRE ATT&CK mapping.
        """
        system_prompt = "You are a cybersecurity expert. Analyze the article and return JSON with keys: summary, actionable_insights, and mitre_attack (list of T-codes)."
        
        if self.use_local:
            try:
                # Prompt engineering for strict JSON output in local models
                prompt = f"Analyze this text and output ONLY valid JSON format. Do not include markdown blocks or any other text.\n\nText: {content}"
                response_text = await self._call_ollama(prompt, system_prompt)
                
                # Cleanup potential markdown ticks from local models
                cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
                result = json.loads(cleaned_text)
                
                return {
                    "summary": result.get("summary", ""),
                    "actionable_insights": result.get("actionable_insights", ""),
                    "mitre_attack": result.get("mitre_attack", [])
                }
            except Exception as e:
                logger.error(f"Ollama analysis failed: {e}")
                return {
                    "summary": "Local AI Analysis Failed.",
                    "actionable_insights": "Manual review recommended.",
                    "mitre_attack": []
                }
                
        # OpenAI Fallback
        if not self.client:
             await asyncio.sleep(1)
             return {"summary": "MOCK Summary", "actionable_insights": "MOCK Insight", "mitre_attack": ["T1566"]}

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "summary": result.get("summary", ""),
                "actionable_insights": result.get("actionable_insights", ""),
                "mitre_attack": result.get("mitre_attack", [])
            }
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {
                "summary": "Error occurred during LLM analysis.",
                "actionable_insights": "Manual review recommended.",
                "mitre_attack": []
            }

    async def generate_answer(self, query: str, context_docs: List[str]) -> str:
        """
        Generates an answer based on the provided context documents.
        """
        context_text = "\n---\n".join(context_docs)
        system_prompt = "You are a cybersecurity expert answering based on provided context."
        prompt = f"Answer the following question based ONLY on the provided news articles. If the answer is not in the context, say that you don't know based on current news.\n\nContext:\n{context_text}\n\nQuestion: {query}\nAnswer:"

        if self.use_local:
            try:
                return await self._call_ollama(prompt, system_prompt)
            except Exception as e:
                return f"Error connecting to local AI: {e}"

        if not self.client:
            return "API key missing and local LLM not configured."

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in generate_answer: {e}")
            return "An error occurred while generating the answer."

llm_service = LLMService()
