# Task: Implement Context Length Truncation and Token Inspection

## Original Requirement

**Title**: Implement context length truncation and token inspection  
**Description**: Enforce safe max context limits and inspect token length and entropy to detect unusual input patterns.  
**Acceptance Criteria**:
* Max context token check with fallback.
* Logging of token entropy for analysis.

**Labels**: `llm`, `security`, `tokenization`

## Analysis

This task focuses on two key security measures for LLM interaction:

1. **Context Length Management**: Preventing context window overflows that could lead to errors, degraded responses, or resource exhaustion.
2. **Token Inspection**: Using statistical properties of token distributions (like entropy) to detect unusual inputs that might indicate attacks.

These measures help mitigate risks like denial-of-service attacks, data exfiltration attempts, and certain types of prompt injections.

### Key Considerations

1. **Model Compatibility**: Different models have different context windows and tokenization schemes.
2. **Performance Impact**: Token analysis should not significantly slow down request processing.
3. **Entropy Baselines**: We need to establish normal entropy ranges for legitimate queries.
4. **Graceful Degradation**: When truncation is necessary, it should preserve the most relevant content.

### Dependencies

- Access to model tokenizers
- Understanding of model context window limitations
- Logging infrastructure for token metrics

## Implementation Steps

1. Create a module for tokenization and token analysis functions.
2. Implement entropy calculation for token sequences.
3. Add logging for token statistics and entropy values.
4. Implement token counting and context window configuration for different model types.
5. Add intelligent truncation strategies for context management.
6. Establish baseline entropy ranges for normal queries.
7. Implement anomaly detection for unusual token patterns.
8. Integrate token analysis and context management into the prompt handling pipeline.
9. Add performance monitoring for token processing.
10. Document configuration options and token handling architecture.
11. Tune entropy thresholds based on real usage data.
12. Add monitoring dashboards for token metrics.

## Token Analysis Module Design

```python
# app/utils/token_analysis.py

import math
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple, Any, Optional
import logging
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

class TokenAnalyzer:
    """Analyzes token sequences for security and optimization purposes."""
    
    def __init__(self, model_name: str):
        """Initialize analyzer with model-specific tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
        
        # Model-specific context limits
        self.context_limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "claude-2": 100000,
            "llama": 4096,
            # Add other models as needed
        }
        
        # Default limit if model not found
        self.default_limit = 4096
        
        # Entropy thresholds based on empirical analysis
        self.entropy_thresholds = {
            "low": 1.5,     # Highly repetitive content
            "normal": 4.5,  # Typical natural language
            "high": 7.0     # Potentially suspicious (high randomness)
        }
    
    def get_max_context_length(self) -> int:
        """Get the maximum context length for the current model."""
        # Extract base model name for matching
        base_model = self.model_name.split('/')[-1].lower()
        
        # Find the matching model in our limits dictionary
        for model_key, limit in self.context_limits.items():
            if model_key in base_model:
                return limit
        
        # Return default if no match found
        logger.warning(f"No context limit found for {self.model_name}, using default {self.default_limit}")
        return self.default_limit
    
    def tokenize(self, text: str) -> List[int]:
        """Tokenize text using the model's tokenizer."""
        return self.tokenizer(text)['input_ids']
    
    def calculate_entropy(self, tokens: List[int]) -> float:
        """
        Calculate Shannon entropy of token sequence.
        Higher values indicate more randomness/information.
        """
        if not tokens:
            return 0.0
            
        # Count token frequencies
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        # Calculate entropy
        entropy = 0.0
        for count in token_counts.values():
            probability = count / total_tokens
            entropy -= probability * math.log2(probability)
            
        return entropy
    
    def analyze_tokens(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return token statistics.
        
        Returns:
            Dict containing token count, entropy, and anomaly flags
        """
        tokens = self.tokenize(text)
        token_count = len(tokens)
        entropy = self.calculate_entropy(tokens)
        
        # Determine entropy category
        entropy_level = "normal"
        if entropy < self.entropy_thresholds["low"]:
            entropy_level = "low"
        elif entropy > self.entropy_thresholds["high"]:
            entropy_level = "high"
            
        # Check if token count approaches context limits
        max_context = self.get_max_context_length()
        context_usage_ratio = token_count / max_context
        
        # Log analysis results
        logger.info(
            f"Token analysis: count={token_count}, entropy={entropy:.2f}, "
            f"level={entropy_level}, usage_ratio={context_usage_ratio:.2f}"
        )
        
        return {
            "token_count": token_count,
            "entropy": entropy,
            "entropy_level": entropy_level,
            "context_usage_ratio": context_usage_ratio,
            "is_anomalous": entropy_level != "normal",
            "requires_truncation": context_usage_ratio > 0.9  # 90% threshold
        }
    
    def truncate_context(self, 
                        system_prompt: str,
                        user_input: str,
                        context_docs: List[Dict[str, str]],
                        max_ratio: float = 0.9) -> Tuple[str, List[Dict[str, str]]]:
        """
        Intelligently truncate context to fit within model limits.
        Prioritizes system prompt and user input over context documents.
        
        Args:
            system_prompt: System instructions
            user_input: User query text
            context_docs: List of context documents
            max_ratio: Maximum portion of context window to use
            
        Returns:
            Tuple of (possibly truncated user input, possibly reduced context docs)
        """
        max_tokens = int(self.get_max_context_length() * max_ratio)
        
        # Reserve tokens for system prompt
        system_tokens = len(self.tokenize(system_prompt))
        available_tokens = max_tokens - system_tokens
        
        if available_tokens <= 0:
            logger.error(f"System prompt exceeds {max_ratio*100}% of context window")
            # Emergency truncation of system prompt would go here
            return user_input, []
        
        # Reserve tokens for user input (prioritized over context)
        user_tokens = len(self.tokenize(user_input))
        if user_tokens > available_tokens * 0.5:  # User input shouldn't use more than half
            # Truncate user input if it's excessively long
            logger.warning(f"User input too long ({user_tokens} tokens), truncating")
            # Implement user input truncation here
            # This is simplified; a real implementation would be more nuanced
            user_input = user_input[:int(len(user_input) * (available_tokens * 0.5 / user_tokens))]
            user_tokens = len(self.tokenize(user_input))
        
        available_tokens -= user_tokens
        
        if available_tokens <= 0:
            logger.warning("No tokens available for context after system prompt and user input")
            return user_input, []
        
        # Allocate remaining tokens to context documents
        # Start with all documents
        total_context_tokens = sum(len(self.tokenize(doc["content"])) for doc in context_docs)
        
        # If context fits, return everything
        if total_context_tokens <= available_tokens:
            return user_input, context_docs
            
        # Need to reduce context
        logger.info(f"Context needs truncation: {total_context_tokens} tokens > {available_tokens} available")
        
        # Sort documents by relevance (if available) or prioritize recent documents
        # This is a placeholder; actual implementation would use relevance scores
        sorted_docs = sorted(context_docs, key=lambda d: d.get("relevance", 0), reverse=True)
        
        # Keep adding documents until we hit the limit
        kept_docs = []
        used_tokens = 0
        
        for doc in sorted_docs:
            doc_tokens = len(self.tokenize(doc["content"]))
            if used_tokens + doc_tokens <= available_tokens:
                kept_docs.append(doc)
                used_tokens += doc_tokens
            else:
                # Try to include a truncated version of this document
                remaining_tokens = available_tokens - used_tokens
                if remaining_tokens > 50:  # Only if we can include something meaningful
                    # Truncate document content
                    truncation_ratio = remaining_tokens / doc_tokens
                    truncated_content = doc["content"][:int(len(doc["content"]) * truncation_ratio)]
                    doc["content"] = truncated_content
                    doc["truncated"] = True
                    kept_docs.append(doc)
                break
        
        logger.info(f"Context truncated: kept {len(kept_docs)} of {len(context_docs)} documents")
        return user_input, kept_docs
```

## Integration with Request Pipeline

The token analyzer should be integrated into the existing request flow:

```python
# Pseudocode for API integration
from app.utils.token_analysis import TokenAnalyzer

# Initialize analyzer at application startup
analyzer = TokenAnalyzer(os.environ.get("LLM_MODEL", "gpt-3.5-turbo"))

@app.before_request
def analyze_request():
    if request.path == "/api/chat" and request.method == "POST":
        user_input = request.json.get("prompt", "")
        
        # Analyze tokens for anomalies
        analysis = analyzer.analyze_tokens(user_input)
        
        # Store analysis in request context
        request.token_analysis = analysis
        
        # Log entropy for monitoring
        current_app.logger.info(
            f"Token entropy: {analysis['entropy']:.2f}, "
            f"level: {analysis['entropy_level']}"
        )
        
        # Flag highly anomalous inputs
        if analysis['entropy_level'] == "high" and analysis['entropy'] > 7.5:
            current_app.logger.warning(f"Suspicious entropy detected: {analysis['entropy']:.2f}")
            # Could implement additional monitoring or blocking here
```
