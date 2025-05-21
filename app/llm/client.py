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
        
        # Validate input
        if not prompt or not isinstance(prompt, str):
            logger.warning("Empty or invalid prompt received")
            return {"answer": "I couldn't understand your question.", "tokens_used": 0, "latency_ms": 0}
            
        try:
            if self.provider == "openai":
                from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
                
                # Add system message for improved guardrails
                system_message = "You are a helpful assistant that answers questions based on the provided context. If you don't know the answer, say so clearly. Do not make up information."
                
                messages = [
                    ChatCompletionSystemMessageParam(role="system", content=system_message),
                    ChatCompletionUserMessageParam(role="user", content=prompt)
                ]
                
                # Handle different model parameter requirements
                try:
                    if self.model.startswith("o4-"):
                        response = openai.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_completion_tokens=512,
                            timeout=30  # Add timeout
                        )
                    else:
                        response = openai.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_tokens=512,
                            timeout=30  # Add timeout
                        )
                    answer = response.choices[0].message.content
                    tokens_used = response.usage.total_tokens if response.usage is not None else None
                except openai.APIConnectionError as e:
                    logger.error(f"OpenAI API connection error: {e}")
                    return {"answer": "I'm having trouble connecting to my knowledge source. Please try again later.", "error": str(e)}
                except openai.RateLimitError as e:
                    logger.error(f"OpenAI rate limit error: {e}")
                    return {"answer": "I'm currently overloaded with requests. Please try again later.", "error": str(e)}
                except openai.APIError as e:
                    logger.error(f"OpenAI API error: {e}")
                    return {"answer": "I encountered an error while processing your question. Please try again.", "error": str(e)}
                    
            elif self.provider == "ollama":
                # Call Ollama local LLM API (e.g., Mistral) with timeout
                try:
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
                        timeout=30  # Add reasonable timeout
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    answer = data.get("message", {}).get("content", "")
                    tokens_used = data.get("eval_count", None)
                except requests.exceptions.Timeout:
                    logger.error("Ollama request timed out")
                    return {"answer": "I'm taking too long to respond. Please try a simpler question or try again later.", "error": "Timeout"}
                except requests.exceptions.RequestException as e:
                    logger.error(f"Ollama request error: {e}")
                    return {"answer": "I'm having trouble connecting to my knowledge source. Please try again later.", "error": str(e)}
            else:
                answer = f"[LLM-{self.provider}]: Unsupported provider"
                tokens_used = None
                
            latency = (time.time() - start) * 1000
            logger.info(f"LLM response generated. Latency: {latency:.2f} ms, Tokens used: {tokens_used}")
            return {"answer": answer, "tokens_used": tokens_used, "latency_ms": latency}
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error(f"Error during LLM generation: {e}", exc_info=True)
            return {
                "answer": "I encountered an unexpected error. Please try again later.",
                "error": str(e),
                "latency_ms": latency
            }
