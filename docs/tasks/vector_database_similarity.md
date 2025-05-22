# Vector Database / Similarity

## Original Requirement

**Title**: Integrate vector DB for prompt similarity search
**Description**:
Store all prompts in a vector DB (e.g., FAISS, Qdrant) and implement semantic similarity checks for detecting near-duplicate attacks.
**Acceptance Criteria**:
* Vector DB integration complete.
* API available to query similar prompts.
* Threshold-based alerting.
**Labels**: `vector-db`, `similarity`, `retrieval`

## Analysis

Vector databases are essential for performing efficient similarity search across large volumes of text data. In this case, we'll use a vector database to store embeddings of user prompts and detect when new prompts have semantic similarity to known attack patterns.

### Key Considerations

1. **Selection of Vector Database**:
   - FAISS, Qdrant, Pinecone, Milvus, and Weaviate are all viable options
   - For our purposes, Qdrant offers a good balance of features, ease of use, and performance
   - Can be self-hosted or used as a managed service

2. **Embedding Model**:
   - Need a high-quality embedding model to convert prompts to vectors
   - Options include OpenAI's text-embedding-ada-002, HuggingFace models like all-MiniLM-L6-v2, or sentence-transformers
   - Choose a model that balances quality, speed, and cost

3. **Integration Architecture**:
   - Need to embed and store all incoming prompts
   - Must be able to query for similar prompts efficiently
   - Should handle batching and asynchronous processing

4. **Threshold Determination**:
   - Need to determine similarity thresholds through empirical testing
   - Different thresholds may be needed for different types of attack patterns
   - Will require an initial training set of known attack patterns

## Implementation Steps

1. Select and deploy a vector database suitable for prompt similarity search.
2. Configure authentication, access controls, and initial collection structure in the vector database.
3. Choose and set up a high-quality embedding model for prompt vectorization.
4. Implement a pipeline to embed and store all incoming prompts in the vector database.
5. Create database schema and indexes for efficient similarity search.
6. Develop REST API endpoints for storing and searching prompt embeddings, including batch processing.
7. Implement asynchronous processing for embedding generation and prompt storage.
8. Add authentication and rate limiting to the API.
9. Implement threshold-based alerting with configurable alert levels and notification channels.
10. Integrate the similarity search system with the existing prompt processing pipeline and logging system.
11. Set up metrics collection and develop an admin dashboard for alerts, threshold configuration, and similarity visualizations.
12. Conduct performance testing and optimize query latency, search parameters, and caching.
13. Create a comprehensive test suite for embedding logic, API endpoints, and vector database integration.
14. Document API usage, system architecture, and operational procedures.

## Technical Specifications

### Vector Database Configuration

#### Qdrant Configuration:
```yaml
storage:
  storage_path: ./storage
  optimizers:
    deleted_threshold: 0.2
    vacuum_min_vector_number: 1000
    default_segment_number: 2
    max_segment_size: 5000
  performance:
    max_search_threads: 0
service:
  http_port: 6333
  grpc_port: 6334
```

### Embedding Model Selection

We'll use the `all-MiniLM-L6-v2` model from sentence-transformers, which offers a good balance of quality and performance. It produces 384-dimensional vectors and can be run locally without API costs.

### API Schema

#### Store Prompt Embedding Request:
```json
{
  "prompt_id": "string",
  "prompt_text": "string",
  "metadata": {
    "user_id": "string",
    "timestamp": "string",
    "source": "string",
    "tags": ["string"]
  }
}
```

#### Search Similar Prompts Request:
```json
{
  "prompt_text": "string",
  "threshold": 0.8,
  "limit": 10
}
```

#### Search Response:
```json
{
  "results": [
    {
      "prompt_id": "string",
      "original_text": "string",
      "similarity_score": 0.95,
      "metadata": {
        "user_id": "string",
        "timestamp": "string",
        "source": "string",
        "tags": ["string"]
      }
    }
  ]
}
```

### Alert Configuration

#### Alert Levels:
- **Low**: 0.8 - 0.89 similarity score
- **Medium**: 0.9 - 0.95 similarity score
- **High**: > 0.95 similarity score

#### Alert Actions:
- **Low**: Log only
- **Medium**: Log + notify team channel
- **High**: Log + notify team channel + create incident

## Resource Requirements

- **Compute**: At least 4 CPU cores, 8GB RAM for vector database
- **Storage**: Initial 20GB for database (scalable)
- **Dependencies**: 
  - Qdrant or similar vector database
  - Sentence-transformers library
  - FastAPI or Flask for API endpoints
  - Redis for job queuing (optional)
- **Development Time**: 3-4 weeks
