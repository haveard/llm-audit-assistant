# Security Module: Handles input sanitization, prompt injection detection, and request rate limiting
#
# This module provides security utilities for the LLM Audit Assistant application:
# 1. Log request sanitization to prevent sensitive data leakage in logs
# 2. Prompt injection detection to prevent attacks against the LLM
# 3. Input/output sanitization to prevent XSS and other injection attacks
# 4. API rate limiting to prevent abuse
#
# These components help ensure the application is resilient against various attack vectors
# and follows security best practices for LLM-based applications.

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
    """
    Log user requests and model responses with appropriate sanitization to avoid log pollution.
    
    This function is called after each successful query to the LLM to record:
    1. The user's question (truncated for readability)
    2. The model's response (truncated for readability)
    3. Summary of sources used (without full content to keep logs manageable)
    
    Args:
        request: The FastAPI request object
        user_input: The user's question text
        model_response: The LLM's response text
        sources: List of document chunks used as context
    """
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
    """
    Detect potential prompt injection attacks by searching for suspicious patterns.
    
    Prompt injection is an attack where malicious users attempt to override system
    instructions or manipulate the LLM's behavior. This function checks for common
    patterns like "ignore previous instructions" that may indicate an attempt to
    bypass system guardrails.
    
    Used as part of the query endpoint to reject potentially malicious prompts.
    
    Args:
        text: User input text to scan for injection attempts
        
    Returns:
        Boolean indicating whether prompt injection was detected
    """
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
    """
    Sanitize and limit user input to prevent injection attacks.
    
    This function applies two important protections:
    1. HTML escaping to prevent XSS if output is later rendered in HTML
    2. Length limits to prevent resource exhaustion attacks
    
    Applied to all user inputs before processing.
    
    Args:
        text: Raw user input text
        max_length: Maximum allowed length (default: 2000 chars)
        
    Returns:
        Sanitized and truncated text
    """
    if not isinstance(text, str):
        return ""
    # HTML escape to prevent XSS if output is rendered in HTML
    text = html.escape(text)
    return text[:max_length]


def sanitize_output(text: str, max_length: int = 4000) -> str:
    """
    Sanitize and limit model output to prevent injection attacks.
    
    Even trusted LLM outputs need sanitization because:
    1. Models can sometimes generate unexpected or malicious content
    2. Outputs may be rendered in HTML contexts where XSS is possible
    3. Excessive output could cause performance issues
    
    Applied to all model outputs before returning to the user.
    
    Args:
        text: Raw LLM output text
        max_length: Maximum allowed length (default: 4000 chars)
        
    Returns:
        Sanitized and truncated text
    """
    if not isinstance(text, str):
        text = str(text)
    # HTML escape to prevent XSS if output is rendered in HTML
    text = html.escape(text)
    return text[:max_length]


def filter_characters(text: str, allowed_pattern: str = r"[\w\s.,;:!?@#%&()\[\]{}\-_'\"]+") -> str:
    """
    Filter text to only contain allowed characters using a regex whitelist.
    
    This provides a more restrictive sanitization than HTML escaping by
    completely removing potentially dangerous characters rather than escaping them.
    
    Used in contexts where strict character filtering is necessary for security.
    
    Args:
        text: Text to filter
        allowed_pattern: Regex pattern of allowed characters
        
    Returns:
        Filtered text containing only allowed characters
    """
    if not isinstance(text, str):
        return ""
    matches = re.findall(allowed_pattern, text)
    return "".join(matches)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that implements IP-based rate limiting for API endpoints.
    
    This middleware tracks request counts per client IP in time windows and returns
    429 Too Many Requests responses when clients exceed their limit. This protects 
    the application from abuse, DoS attacks, and excessive resource consumption.
    
    The middleware is applied in app/main.py to protect all API endpoints.
    """
    
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize the rate limiter middleware.
        
        Args:
            app: FastAPI application instance
            max_requests: Maximum allowed requests per time window
            window_seconds: Size of the time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        """
        Process each incoming request to check against rate limits.
        
        This method:
        1. Identifies the client by IP address
        2. Assigns the request to a time window
        3. Counts requests per client per window
        4. Either allows the request to proceed or returns 429
        
        Args:
            request: The FastAPI request object
            call_next: Async function to call next middleware/route handler
            
        Returns:
            Either the response from the next handler or a 429 response
        """
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
