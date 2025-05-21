# OpenAI/Local LLM integration

import os
import time
import logging

import openai
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("llm_audit_assistant.llm_client")


class LLMClient:
    def __init__(self, provider: str = "openai", model: str = "", ollama_url: str = ""):
        self.provider = provider
        self.model = model or ("o4-mini" if provider == "openai" else "mistral")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        logger.info(f"Initialized LLMClient with provider={self.provider}, model={self.model}")
        if self.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY not set in environment or .env file.")
            raise ValueError("OPENAI_API_KEY not set in environment or .env file.")

    def generate(self, prompt: str) -> dict:
        start = time.time()
        logger.info(f"Generating LLM response for prompt (length={len(prompt)}). Provider: {self.provider}")
        try:
            if self.provider == "openai":
                from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

                messages = [
                    ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant."),
                    ChatCompletionUserMessageParam(role="user", content=prompt)
                ]
                if self.model.startswith("o4-"):
                    response = openai.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_completion_tokens=512
                    )
                else:
                    response = openai.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=512
                    )
                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage is not None else None
            elif self.provider == "ollama":
                # Call Ollama local LLM API (e.g., Mistral)
                resp = requests.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    },
                    timeout=60
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("message", {}).get("content", "")
                tokens_used = data.get("eval_count", None)
            else:
                answer = f"[LLM-{self.provider}]: {prompt}"
                tokens_used = None
            latency = (time.time() - start) * 1000
            logger.info(f"LLM response generated. Latency: {latency:.2f} ms, Tokens used: {tokens_used}")
            return {"answer": answer, "tokens_used": tokens_used, "latency_ms": latency}
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}", exc_info=True)
            raise
