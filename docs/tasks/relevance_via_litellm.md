# Relevance via LiteLLM

## Original Requirement

**Title**: Integrate relevance scoring via LiteLLM
**Description**:
Score each prompt-response pair for relevance using LiteLLM to filter or reroute irrelevant chains.
**Acceptance Criteria**:
* LiteLLM scoring functional.
* Irrelevant prompts flagged or dropped.
**Labels**: `relevance`, `liteLLM`, `response-quality`

## Analysis

Relevance scoring is crucial for ensuring LLM outputs actually address the input prompts. Irrelevant responses can indicate various issues, including prompt injection attempts, model hallucinations, or context confusion. By implementing relevance scoring with LiteLLM, we can detect and mitigate these issues, improving the overall quality and security of LLM interactions.

### Key Considerations

1. **LiteLLM Integration**:
   - LiteLLM provides a unified interface for multiple LLM providers
   - Can be used for routing, fallbacks, and evaluation
   - Supports major providers (OpenAI, Anthropic, etc.)
   - Handles rate limiting, retries, and error handling

2. **Relevance Scoring Methods**:
   - Direct LLM evaluation (asking an LLM to score relevance)
   - Embedding similarity between prompt and response
   - Hybrid approaches combining multiple signals
   - Fine-tuned specialized scoring models

3. **Implementation Options**:
   - Post-processing evaluation after response generation
   - Streaming evaluation during generation
   - Batch evaluation for analytics and quality monitoring
   - Real-time evaluation for immediate action

4. **Response Actions**:
   - Filtering out irrelevant responses
   - Rerouting to alternative models when relevance is low
   - Providing feedback to users about low relevance
   - Logging for quality monitoring and improvement

## Implementation Steps

- Set up LiteLLM integration, including provider configurations, API keys, and a testing environment.
- Implement a relevance evaluator using LiteLLM, supporting direct LLM evaluation, embedding similarity, and hybrid approaches.
- Design and implement a batching system for embedding calculations, caching strategy for common prompts, and optimization for throughput and cost efficiency.
- Implement a relevance processor to evaluate prompt-response pairs, determine actions based on relevance, and log evaluations.
- Integrate the relevance evaluation system with the API layer, providing endpoints for evaluation and fallback handling.
- Create a comprehensive test suite for evaluator components, processor integration, performance, and A/B testing.
- Set up a feedback loop for user feedback collection, evaluation improvements, and periodic review of thresholds.
- Optimize evaluation prompts for accuracy, test with different models, and create specialized templates for different domains.
- Implement transparent evaluation by providing explanations of relevance scores, visualizations, and confidence metrics.
- Create comprehensive documentation, including architecture diagrams, configuration guides, performance tips, and monitoring guidance.

## Technical Specifications

### LiteLLM Configuration

```python
# Example LiteLLM configuration
litellm.set_verbose = True  # For debugging

# Configure provider settings
litellm_config = {
    "default_fallback_models": ["gpt-4", "claude-v1"],
    "timeout": 30,  # 30 seconds timeout
    "max_retries": 3,
    "cache": {
        "type": "redis",
        "host": "redis-cache",
        "port": 6379,
        "ttl": 3600  # 1 hour cache
    },
    "api_key": {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY")
    }
}
```

### Evaluation Methods

| Method | Description | Pros | Cons |
|--------|-------------|------|------|
| LLM Evaluation | Uses another LLM to score relevance | High quality judgments, understands nuance | Higher cost, slower |
| Embedding Similarity | Uses cosine similarity of embeddings | Fast, low cost, quantitative | Less nuanced, sensitive to wording |
| Hybrid | Combines both methods | More robust, balances speed and quality | More complex, higher cost than embeddings alone |

### Relevance Scoring Scale

| Score Range | Classification | Recommended Action |
|-------------|----------------|-------------------|
| 0.0 - 0.3 | Irrelevant | Reject and log |
| 0.3 - 0.5 | Low Relevance | Reject or reroute to stronger model |
| 0.5 - 0.7 | Moderate Relevance | Accept with caution, monitor |
| 0.7 - 1.0 | High Relevance | Accept |

### LLM Evaluation Prompt

The evaluation prompt is designed to be:
1. Clear and concise
2. Specific about the evaluation criteria
3. Structured for consistent numerical responses

```
You are an expert evaluator of LLM responses. Your task is to evaluate the relevance of a response to a given prompt.

Prompt: {prompt}

Response: {response}

On a scale of 0 to 10, where:
- 0 means completely irrelevant, the response has nothing to do with the prompt
- 5 means partially relevant, the response addresses some aspects of the prompt but misses key points
- 10 means perfectly relevant, the response directly and completely addresses the prompt

Provide your evaluation as a single number between 0 and 10, with no other text.
```

### Log Format

```json
{
  "timestamp": "2023-09-15T14:32:10.123456Z",
  "prompt_id": "prompt-123456",
  "prompt_snippet": "How do I configure my network settings in Linux?...",
  "response_snippet": "To configure network settings in Linux, you can use the following commands...",
  "relevance_score": 0.85,
  "evaluation_method": "hybrid",
  "llm_score": 0.9,
  "embedding_score": 0.75,
  "is_relevant": true,
  "action": "accept",
  "processing_time_ms": 245,
  "model_info": {
    "evaluation_model": "gpt-3.5-turbo",
    "embedding_model": "text-embedding-ada-002",
    "fallback_model": "gpt-4"
  }
}
```

### Performance Considerations

1. **Batching**:
   - Process multiple evaluations in parallel
   - Use batched embedding requests
   - Queue non-urgent evaluations during high load

2. **Caching**:
   - Cache evaluation results for similar prompt-response pairs
   - Cache embeddings for frequent prompts
   - Implement TTL for cached results

3. **Async Processing**:
   - Use background tasks for non-blocking operation
   - Implement full async pipeline
   - Provide webhooks for completion notification

4. **Cost Optimization**:
   - Use embedding similarity as first-pass filter
   - Only use LLM evaluation for borderline cases
   - Downgrade to smaller models for routine evaluation

## Resource Requirements

- **Compute**:
  - 2-4 CPU cores for API processing
  - Memory: 4GB RAM minimum
  - No specific GPU requirements
- **Storage**:
  - Log storage: Initially 5GB, scaling with usage
  - Cache storage: 2-5GB depending on traffic volume
- **Dependencies**:
  - litellm
  - fastapi
  - numpy
  - redis (for caching)
  - aiohttp (for async HTTP requests)
