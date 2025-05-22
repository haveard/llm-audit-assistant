# Prompt-Response Similarity

## Original Requirement

**Title**: Implement prompt-response similarity scoring
**Description**:
Compute cosine similarity between prompt and response embeddings to detect prompt leakage or excessive influence.
**Acceptance Criteria**:
* Embedding model integrated.
* Scores logged and threshold-tuned.
**Labels**: `similarity`, `response-analysis`, `leakage-detection`

## Analysis

Measuring the similarity between prompts and their corresponding responses can help detect potential security issues such as prompt leakage or excessive influence of the prompt on the response. This is particularly useful for identifying cases where confidential instructions are being leaked or where the model is simply regurgitating input rather than providing useful outputs.

### Key Considerations

1. **Embedding Model Selection**:
   - Need a high-quality embedding model that captures semantic meaning
   - Model should be efficient enough for production use
   - Options include OpenAI embeddings, sentence-transformers, or custom fine-tuned models

2. **Similarity Metrics**:
   - Cosine similarity is the standard for comparing embeddings
   - May want to consider other metrics (Euclidean distance, dot product)
   - Need to establish baseline thresholds for different types of interactions

3. **Implementation Approach**:
   - Need to embed both prompts and responses
   - Should split long texts into chunks for more accurate comparison
   - Need to handle multi-turn conversations appropriately

4. **Integration Points**:
   - Should be integrated into the LLM response processing pipeline
   - Scores need to be logged for analysis
   - Alerts should be triggered for unusually high similarity scores

## Implementation Steps

- Select and integrate an embedding model for prompt-response similarity analysis, and set up infrastructure for efficient embedding generation and model swapping.
- Implement caching and optimization for frequently used embeddings, batch processing, and background processing.
- Create an analysis pipeline to analyze historical prompt-response pairs, establish baseline similarity distributions, and determine appropriate thresholds for different contexts.
- Implement adaptive thresholding with dynamic adjustment, handling of labeled/unlabeled data, and threshold optimization using historical data.
- Develop visualization and analysis tools for similarity distributions, false positive/negative analysis, and feedback mechanisms for threshold improvement.
- Integrate similarity scoring with the LLM response processing pipeline, including pre/post processing and monitoring.
- Implement a logging system with structured format, storage for similarity scores, and retention policies.
- Create an alerting mechanism with defined thresholds, notification channels, and alert suppression.
- Conduct performance testing to measure latency, optimize for production workloads, and implement batching for efficiency.
- Refine detection accuracy by analyzing false positives/negatives, adjusting thresholds, and implementing context-specific thresholds.
- Document the system, including technical documentation, tuning process, and user guides for the security team.

## Technical Specifications

### Embedding Model Selection

After evaluating various options, we recommend using **all-mpnet-base-v2** from sentence-transformers as it offers an excellent balance of accuracy and performance. This model:

- Produces 768-dimensional embeddings
- Achieves high performance on semantic similarity tasks
- Can run efficiently on CPU for production workloads
- Has relatively low memory requirements (around 420MB)

### Similarity Scoring Algorithm

1. **Text Preprocessing**:
   - Normalize text (lowercase, remove extra whitespace)
   - Split into chunks for detailed analysis
   - Handle special tokens and formatting

2. **Embedding Generation**:
   - Generate embeddings for prompt and response chunks
   - Cache embeddings for frequent prompts/responses

3. **Similarity Calculation**:
   - Compute cosine similarity between vectors
   - Analyze both overall similarity and chunk-by-chunk similarity
   - Identify highest similarity segments

### Threshold Configuration

| Use Case | Default Threshold | Rationale |
|----------|-------------------|-----------|
| General Conversation | 0.8 | Based on empirical testing of normal conversations |
| Sensitive Instructions | 0.7 | Lower threshold for higher security |
| Technical Documentation | 0.85 | Technical responses naturally more similar to prompts |
| Creative Content | 0.6 | Creative responses should differ from prompts |

### Log Format

```json
{
  "timestamp": "2023-09-15T14:32:10.123456Z",
  "prompt_id": "prompt-123456",
  "overall_similarity": 0.65,
  "max_chunk_similarity": 0.82,
  "suspicious": true,
  "threshold": 0.8,
  "chunk_info": {
    "chunk_count": 3,
    "max_similarity_chunk_index": 1,
    "chunk_similarities": [0.45, 0.82, 0.62]
  },
  "metadata": {
    "model_name": "all-mpnet-base-v2",
    "prompt_length": 120,
    "response_length": 450
  }
}
```

### Alert Configuration

| Alert Level | Trigger | Action |
|-------------|---------|--------|
| High | Similarity > threshold + 0.1 | Block response, notify security team |
| Medium | Similarity > threshold | Log, flag for review |
| Low | Similarity > threshold - 0.1 | Log only |

### Performance Considerations

- **Batching**: Process multiple similarity checks in batches for efficiency
- **Caching**: Cache embeddings for frequently used prompts and responses
- **Async Processing**: Use asynchronous processing to avoid blocking
- **Sampling**: For very long responses, can use sampling to reduce computation

## Resource Requirements

- **Compute**:
  - Moderate CPU requirements for embedding generation
  - GPU optional but beneficial for high-volume processing
- **Memory**: Approximately 1GB RAM for model and processing
- **Storage**:
  - Model size: ~420MB
  - Log storage: Initially 5GB, scaling with usage
- **Dependencies**:
  - sentence-transformers
  - numpy
  - torch (optional for GPU support)
