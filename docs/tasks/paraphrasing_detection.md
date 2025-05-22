# Paraphrasing Detection

## Original Requirement

**Title**: Detect paraphrased variants of known prompt attacks
**Description**:
Use paraphrase detection to flag semantically similar adversarial prompts that evade regex/YARA.
**Acceptance Criteria**:
* Embedding or paraphrase model integrated.
* Paraphrased variants matched against blacklist.
**Labels**: `paraphrasing`, `evasion`, `detection`

## Analysis

Adversaries often attempt to bypass security measures by paraphrasing known attack patterns. Traditional pattern matching methods like regex and YARA rules can be easily evaded through simple rewording while preserving the semantic intent of the attack. Implementing robust paraphrase detection allows us to identify these semantically equivalent attacks, providing a more resilient defense against prompt injection and other adversarial techniques.

### Key Considerations

1. **Detection Approach Selection**:
   - Embedding-based similarity detection
   - Specialized paraphrase detection models
   - Transformer models fine-tuned for semantic equivalence
   - Combination of multiple approaches for robustness

2. **Blacklist Management**:
   - Database of known attack patterns and their semantic representations
   - Clustering of related attacks
   - Versioning and update mechanisms
   - Sensitivity and threshold configuration

3. **Performance and Scalability**:
   - Processing time constraints for real-time detection
   - Optimization techniques for large blacklists
   - Batching and caching strategies
   - Vector database integration

4. **Evasion Resistance**:
   - Handling of subtle semantic shifts
   - Addressing cross-lingual paraphrasing
   - Detecting adversarial perturbations
   - Contextual understanding of attack intent

## Implementation Steps

- Implement embedding-based detection by selecting an appropriate embedding model, creating a vectorization pipeline, implementing similarity comparison logic, and establishing detection thresholds.
- Create a blacklist manager with a storage structure for attack patterns, CRUD operations, backup and restore mechanisms, and entry validation.
- Implement vector database storage by choosing and integrating a vector database, creating a persistence layer for the blacklist, and enabling efficient similarity search.
- Create an API for the detection system with RESTful endpoints for checking text, batch processing, blacklist management, authentication, and rate limiting.
- Implement a test suite with paraphrase test sets, detection accuracy measurement, performance testing, and evaluation of false positive/negative rates.
- Optimize for performance by implementing batching, caching, and efficient similarity calculations.
- Implement clustering for attack variants, including algorithms for grouping related attacks, visualization of clusters, and automatic labeling of new patterns.
- Expand the blacklist by creating tools to generate attack variants, developing a UI for manual variant creation, and enabling bulk import/export.
- Set up monitoring and alerting with metrics collection, alert systems for detection events, and trend analysis for attack patterns.
- Optimize for scale by benchmarking with large blacklists, implementing sharding for distributed deployment, and creating efficient update mechanisms.
- Build an admin interface for blacklist management, visualization of attack clusters, and audit logging for changes.
- Create documentation, including system architecture, deployment guides, tuning recommendations, and integration examples.

## Technical Specifications

### Model Selection

After evaluating various options, we recommend using `sentence-transformers/all-MiniLM-L6-v2` as the primary embedding model for paraphrase detection. This model offers:

- Good balance of performance and accuracy
- 384-dimensional embeddings
- Support for 100+ languages
- Fast inference suitable for production
- Small model size (~80MB)

For more sensitive applications, `sentence-transformers/all-mpnet-base-v2` provides higher accuracy at the cost of increased resource requirements.

### Similarity Thresholds

Based on empirical testing, we recommend the following thresholds:

| Threshold | Description | Use Case |
|-----------|-------------|----------|
| 0.85+ | Very high similarity | Default setting, low false positives |
| 0.80 - 0.85 | High similarity | Balanced detection |
| 0.75 - 0.80 | Moderate similarity | Sensitive applications, higher false positives |
| < 0.75 | Low similarity | Not recommended, excessive false positives |

### Vector Database Options

| Database | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| FAISS | Fast, mature, highly optimized | C++ with Python bindings, harder to deploy | Best for high performance needs |
| Qdrant | Pure Rust, filtering capabilities, cloud option | Newer project | Good balance of features and simplicity |
| Milvus | Highly scalable, cloud option | More complex setup | Best for very large deployments |
| Pinecone | Fully managed, simple API | Cost, vendor lock-in | Best for quick deployment without ops overhead |

### Blacklist Entry Schema

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "original attack pattern text",
  "embedding": [0.23, -0.15, ...],  // 384-dimensional vector
  "attack_type": "prompt_injection",
  "added_at": "2023-09-15T14:32:10.123456Z",
  "added_by": "user@example.com",
  "source": "manual",  // manual, automated, imported
  "status": "active",  // active, deprecated, testing
  "detection_count": 12,  // how many times this pattern was detected
  "last_detected": "2023-10-20T09:45:22.123456Z",
  "metadata": {
    "severity": "high",
    "description": "Attempts to bypass system instructions",
    "tags": ["system-prompt", "instruction-override"],
    "mitre_attack": "T1566",
    "examples": [
      "alternative pattern 1",
      "alternative pattern 2"
    ]
  }
}
```

### API Endpoints

#### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Check text against blacklist |
| `/batch-check` | POST | Check multiple texts in batch |
| `/blacklist` | POST | Add entry to blacklist |
| `/blacklist/{id}` | GET | Retrieve blacklist entry |
| `/blacklist/{id}` | DELETE | Remove entry from blacklist |
| `/blacklist/import` | POST | Bulk import entries |
| `/blacklist/export` | GET | Export all entries |

#### Analytics Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/clusters` | GET | Get attack pattern clusters |
| `/suggestions` | POST | Get variant suggestions |
| `/stats` | GET | Get detection statistics |
| `/visualize` | GET | Generate embedding visualization |

### Performance Optimizations

1. **Batch Processing**:
   - Process multiple texts in single API call
   - Batch embedding generation for efficiency
   - Parallelize similarity comparisons

2. **Approximate Nearest Neighbor (ANN)**:
   - Use ANN algorithms for large blacklists
   - Trade perfect accuracy for speed
   - Implement HNSW or IVF indexing

3. **Caching Strategy**:
   - Cache results for frequent checks
   - Cache embeddings for common inputs
   - Use LRU cache with appropriate TTL

4. **Distributed Processing**:
   - Shard blacklist across multiple nodes
   - Implement request routing based on load
   - Use consistent hashing for sharding

## Resource Requirements

- **Compute**:
  - RAM: 4-8GB minimum (scales with blacklist size)
  - CPU: 4+ cores recommended
  - GPU: Optional but beneficial for high throughput
- **Storage**:
  - Model size: ~80MB
  - Vector database: Scales with blacklist size (~1MB per 1000 entries plus overhead)
- **Dependencies**:
  - transformers
  - torch
  - numpy
  - fastapi
  - vector database client (qdrant-client, pinecone, etc.)
