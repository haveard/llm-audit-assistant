# Canary Tokens

## Original Requirement

**Title**: Deploy canary tokens to detect LLM output leaks
**Description**:
Embed identifiable canary strings into system prompts or training data to detect model exfiltration.
**Acceptance Criteria**:
* Canary tokens inserted.
* Monitoring in place for response leaks.
**Labels**: `canary`, `monitoring`, `llm-leakage`

## Analysis

Canary tokens are unique, identifiable strings that can be embedded into sensitive data to detect when that data has been leaked or accessed improperly. For LLMs, these tokens can help identify if system prompts, training data, or other sensitive information has been leaked through model outputs or been inappropriately accessed.

### Key Considerations

1. **Canary Token Design**:
   - Tokens need to be unique and identifiable
   - Should be difficult to explicitly filter out
   - Should not significantly impact model performance
   - Need to balance detectability with subtlety

2. **Deployment Strategies**:
   - System prompt injection
   - Training data watermarking
   - Context window inclusion
   - Fine-tuning dataset inclusion

3. **Detection Methods**:
   - Direct string matching
   - Fuzzy matching for partially leaked tokens
   - External monitoring services
   - Regular scanning of public repositories

4. **Response to Detection**:
   - Alerting mechanisms
   - Incident response procedures
   - Token rotation and refresh policies
   - Legal and compliance considerations

## Implementation Steps

- Design a unique and identifiable canary token format that is resilient to common transformations and appears natural in context.
- Specify requirements for a canary token generator, including expected inputs, outputs, and configuration options.
- Design the schema and requirements for a token tracking database, including metadata, registration, management, and status updates.
- Specify requirements and strategies for injecting canary tokens into system prompts, including different injection modes and token registration.
- Specify requirements and strategies for injecting canary tokens into fine-tuning datasets, including placement strategies and quality criteria.
- Specify requirements for monitoring infrastructure, including web hooks, external scanning services, and logging/alerting systems for canary tokens.
- Specify requirements for a token detection system, including exact and fuzzy matching, context extraction, and detection reporting.
- Implement an alert management system with notification channels, escalation policies, and incident response workflows.
- Implement automated scanning, including scheduled repository scans, web scraping for public sites, and monitoring of code hosting platforms.
- Conduct penetration testing to evaluate token detection effectiveness, evasion resistance, and refine detection mechanisms.
- Create comprehensive documentation for token formats, generation, incident response, and integration points with LLM systems.
- Train team members on detection and response, token deployment, and general awareness.

## Technical Specifications

### Canary Token Design

#### Token Formats

1.  **UUID Format**:
    *   Example: `CANARY-f7d1-b3a2-e9c4`
    *   Use: System prompts, fine-tuning data
    *   Characteristics: Easily identifiable, structured

2.  **Natural Language Format**:
    *   Example: `confidential-a7b3c9d2e5f8`
    *   Use: Training data, conversational contexts
    *   Characteristics: Blends better into text

3.  **Organization Format**:
    *   Example: `CN-ACME-x9y8z7w6`
    *   Use: Cross-organization tracking
    *   Characteristics: Includes organization identifier

#### Token Metadata

All tokens contain embedded metadata that can be extracted from the token value:
- Organization ID
- Token ID (UUID)
- Creation timestamp
- Expiration date (optional)
- Token type
- Source system

### Token Repository Schema Task
    *   Define the structure and fields for a database or system to store and manage canary token information.
    *   Include fields for token ID, value, type, status, creation/expiration dates, detection counts, and related metadata.

### Detection Methods and Confidence

| Detection Method | Description | Confidence Range |
|-----------------|-------------|-----------------|
| Exact Match | Token found exactly as registered | 100% |
| Fuzzy Match | Token found with minor variations | 90-99% |
| Partial Match | Fragment of token detected | 70-89% |
| Pattern Match | Token format detected | 50-69% |

### Alert Levels and Actions

| Alert Level | Trigger | Action |
|-------------|---------|--------|
| Critical | Exact match in public repository | Immediate notification, incident response |
| High | Exact match in model output | Notification within 15 minutes, investigation |
| Medium | Fuzzy match above 90% | Daily summary report |
| Low | Pattern match | Weekly summary report |

### Monitoring Infrastructure

1. **Web Hooks**:
   - REST API endpoints for external service reporting
   - Webhook authentication and validation
   - Rate limiting and abuse prevention

2. **Scheduled Scanning**:
   - Daily scans of public GitHub repositories
   - Weekly scans of common ML model sharing platforms
   - Monthly scans of academic paper repositories

3. **Realtime Monitoring**:
   - Integration with LLM serving infrastructure
   - Output scanning for production LLM endpoints
   - Logging of all token detections

## Resource Requirements

- **Compute**: Low - primarily for scanning and detection
- **Storage**: 
  - Token database: <1GB
  - Detection logs: Initially 5GB, scaling with usage
- **Dependencies**:
  - Fuzzy matching library (rapidfuzz)
  - Database for token storage (PostgreSQL recommended)
  - Alerting infrastructure (e.g., PagerDuty, Slack webhooks)
