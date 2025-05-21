# Prompt injection filters, sanitization

import html
import logging
import re
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("llm_audit_assistant")
logging.basicConfig(level=logging.INFO)


async def log_request(request: Request, user_input: str, model_response: str, sources=None):
    """Log user request and model response with appropriate sanitization"""
    # Truncate long inputs for log readability
    truncated_input = user_input[:500] + "..." if len(user_input) > 500 else user_input
    truncated_response = model_response[:500] + "..." if len(model_response) > 500 else model_response
    
    logger.info(f"User input: {truncated_input}")
    logger.info(f"Model response: {truncated_response}")
    if sources:
        # Avoid logging full sources content, just the count and metadata
        source_count = len(sources)
        source_meta = [s.get("metadata", "") for s in sources]
        logger.info(f"Sources: {source_count} chunks, metadata: {source_meta}")


def scan_prompt_injection(text: str) -> bool:
    """More comprehensive prompt injection detection"""
    # Simple regex-based prompt injection detection
    patterns = [
        r"ignore previous instructions",
        r"forget previous",
        r"you are now",
        r"repeat after me",
        r"/system",
        r"system prompt",
        r"ignore constraints",
        r"new instructions",
        r"overwrite instructions"
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Sanitize and limit input size, with HTML escaping"""
    if not isinstance(text, str):
        return ""
    # HTML escape to prevent XSS if output is rendered in HTML
    text = html.escape(text)
    return text[:max_length]


def sanitize_output(text: str, max_length: int = 4000) -> str:
    """Sanitize and limit output size, with HTML escaping"""
    if not isinstance(text, str):
        text = str(text)
    # HTML escape to prevent XSS if output is rendered in HTML
    text = html.escape(text)
    return text[:max_length]


def filter_characters(text: str, allowed_pattern: str = r"[\w\s.,;:!?@#%&()\[\]{}\-_'\"]+") -> str:
    """Remove disallowed characters"""
    if not isinstance(text, str):
        return ""
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
