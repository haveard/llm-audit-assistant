# Prompt injection filters, sanitization

import logging
import re
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("llm_audit_assistant")
logging.basicConfig(level=logging.INFO)


async def log_request(request: Request, user_input: str, model_response: str, sources=None):
    logger.info(f"User input: {user_input}")
    logger.info(f"Model response: {model_response}")
    if sources:
        logger.info(f"Sources: {sources}")


def scan_prompt_injection(text: str) -> bool:
    # Simple regex-based prompt injection detection
    patterns = [
        r"ignore previous instructions",
        r"forget previous",
        r"you are now",
        r"repeat after me",
        r"/system",
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def sanitize_input(text: str, max_length: int = 2000) -> str:
    # Escape and limit input size
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text[:max_length]


def sanitize_output(text: str, max_length: int = 4000) -> str:
    # Escape and limit output size
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text[:max_length]


def filter_characters(text: str, allowed_pattern: str = r"[\w\s.,;:!?@#%&()\[\]{}\-_'\"]+") -> str:
    # Remove disallowed characters
    matches = re.findall(allowed_pattern, text)
    return "".join(matches)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = int(now // self.window_seconds)
        key = (client_ip, window)
        self.clients.setdefault(key, 0)
        self.clients[key] += 1
        if self.clients[key] > self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        response = await call_next(request)
        return response
