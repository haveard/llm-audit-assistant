# Sentiment Analysis

## Original Requirement

**Title**: Add sentiment analysis filter to input pipeline
**Description**:
Use a sentiment classifier to detect toxic, aggressive, or manipulative prompt tone.
**Acceptance Criteria**:
* Toxicity score calculated for every prompt.
* Routing or alerting for extreme values.
**Labels**: `nlp`, `filtering`, `sentiment-analysis`

## Analysis

Sentiment analysis can serve as an important first-line defense against harmful or manipulative prompts. By analyzing the tone and emotional content of user inputs, we can detect potentially problematic interactions before they reach the LLM, allowing for appropriate routing, flagging, or blocking of concerning content.

### Key Considerations

1. **Model Selection**:
   - Pre-trained sentiment classifiers (BERT, RoBERTa, DistilBERT)
   - Specialized toxicity models (Perspective API, Detoxify)
   - Multilingual support requirements
   - Performance and latency constraints

2. **Detection Categories**:
   - Toxicity (hate speech, profanity)
   - Aggression/hostility
   - Manipulation techniques
   - Emotional distress
   - Threats or harmful intent

3. **Integration Approach**:
   - Preprocessing step in prompt pipeline
   - Asynchronous analysis for non-blocking operation
   - Caching for similar prompts
   - Threshold configuration for different contexts

4. **Response Actions**:
   - Prompt rejection for severe cases
   - Warning/notification to users
   - Logging and monitoring
   - Escalation to human review

## Implementation Steps

- Research and select appropriate sentiment, toxicity, and emotion detection models, evaluating their performance and latency.
- Implement a model wrapper for each selected model to standardize input/output and support efficient inference.
- Create a combined analyzer that aggregates results from sentiment, toxicity, and emotion models, applies thresholds, and determines recommended actions.
- Integrate the analyzer into the input pipeline, supporting asynchronous analysis, caching, and configurable thresholds for different contexts.
- Implement alerting and routing logic to trigger warnings, block prompts, or escalate based on severity, and log all results.
- Set up structured logging and metrics collection, create dashboards for monitoring, and configure alerting thresholds.
- Develop a comprehensive test suite for analyzer components, pipeline integration, and performance.
- Integrate the sentiment analysis system with the main application, ensuring proper API endpoints and response handling.
- Optimize performance through batching, model quantization, and efficient inference.
- Fine-tune thresholds and actions based on real data, user feedback, and domain-specific requirements.
- Implement a user feedback loop to improve model performance and reduce false positives/negatives.
- Prepare for production deployment with documentation, monitoring, scaling configuration, and alerting setup.

## Technical Specifications

### Model Selection

After evaluating various options, we recommend using the following models:

1. **Toxicity Detection**: `unitary/toxic-bert`
   - Specialized for detecting toxic content
   - Provides multiple toxicity categories
   - Good balance of accuracy and performance

2. **Sentiment Analysis**: `distilbert-base-uncased-finetuned-sst-2-english`
   - General sentiment classification (positive/negative)
   - Lightweight and fast
   - Good for initial sentiment filtering

3. **Emotion Detection**: `bhadresh-savani/distilbert-base-uncased-emotion`
   - Detects specific emotions (anger, fear, etc.)
   - Useful for identifying concerning emotional content
   - Complements general sentiment analysis

### Thresholds and Actions

| Metric | Low | Medium | High | Critical |
|--------|-----|--------|------|----------|
| Overall Toxicity | <0.4 | 0.4-0.6 | 0.6-0.8 | >0.8 |
| Negative Sentiment | <0.6 | 0.6-0.8 | 0.8-0.9 | >0.9 |
| Anger | <0.5 | 0.5-0.7 | 0.7-0.85 | >0.85 |
| Threat | <0.3 | 0.3-0.5 | 0.5-0.7 | >0.7 |

#### Actions by Severity:

- **Critical**: Block prompt, send immediate alert, log incident
- **High**: Block prompt, log incident
- **Medium**: Allow with warning, monitor interaction
- **Low**: Allow, normal logging

### Integration Points

1. **API Gateway**:
   - Analyze requests before reaching LLM
   - Block or flag based on analysis
   - Add analysis metadata to request context

2. **Async Analysis**:
   - Process in parallel with LLM to reduce latency
   - Update response handling based on results
   - Allow early termination for critical issues

3. **Feedback Loop**:
   - Collect data on false positives/negatives
   - Use feedback to improve thresholds
   - Periodically retrain custom models if needed

### Log Format

```json
{
  "timestamp": "2023-09-15T14:32:10.123456Z",
  "event_type": "sentiment_analysis",
  "prompt_id": "prompt-123456",
  "toxicity_scores": {
    "overall_toxicity": 0.82,
    "toxicity": 0.85,
    "severe_toxicity": 0.32,
    "obscene": 0.15,
    "threat": 0.05,
    "insult": 0.76,
    "identity_attack": 0.08
  },
  "sentiment_scores": {
    "positive": 0.12,
    "negative": 0.88
  },
  "emotion_scores": {
    "sadness": 0.05,
    "joy": 0.03,
    "love": 0.02,
    "anger": 0.78,
    "fear": 0.10,
    "surprise": 0.02,
    "negative_emotion": 0.93
  },
  "flags": ["high_toxicity", "very_negative", "high_anger"],
  "action": "block",
  "prompt_snippet": "You stupid [censored] I'm going to [censored]...",
  "severity": "critical"
}
```

### Performance Considerations

- **Batching**: Process multiple inputs in batches for higher throughput
- **Model Quantization**: Use INT8 quantization for production deployment
- **Caching**: Cache results for identical or very similar prompts
- **Async Processing**: Run analysis in parallel with other processing steps
- **Model Serving**: Use optimized inference servers (e.g., ONNX Runtime, TorchServe)

## Resource Requirements

- **Compute**:
  - Inference: 2-4 CPU cores or 1 GPU for high throughput
  - Memory: 4-8GB RAM
- **Storage**:
  - Models: ~500MB per model
  - Logs: Initially 5GB, scaling with usage
- **Dependencies**:
  - PyTorch or TensorFlow
  - transformers library
  - FastAPI for API endpoints
  - Redis for caching (optional)

