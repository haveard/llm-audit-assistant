# Task: Create Taxonomy and Log Structure for Prompt-Based Attacks

## Original Requirement

**Title**: Create taxonomy and log structure for prompt-based attacks  
**Description**: Develop a schema for logging and classifying detected adversarial attacks (e.g., evasion, prompt injection, context abuse).  
**Acceptance Criteria**:
* JSON schema for attack events.
* Logged entries with timestamps, prompt content, severity.

**Labels**: `security`, `logging`, `threat-model`

## Analysis

A comprehensive attack taxonomy and logging structure is foundational for defending against adversarial prompts. This task involves creating a standardized way to classify and record detected attack attempts, enabling better analysis, reporting, and defense improvements over time.

### Key Considerations

1. **Taxonomy Completeness**: The classification system must cover all known attack types while being extensible for new threats.
2. **Log Structure**: Logs must contain sufficient information for forensic analysis without exposing sensitive data.
3. **Performance Impact**: Logging should have minimal impact on system performance and response times.
4. **Regulatory Compliance**: Consider GDPR and other regulatory requirements around logging user data.

### Dependencies

- Basic understanding of current LLM attack vectors
- Logging infrastructure (appears to be Loki based on the project structure)
- Security policies regarding data retention and PII handling

## Implementation Steps

- Research and document attack types by reviewing academic literature and industry reports on LLM attacks, compiling a comprehensive list of attack categories and techniques, and documenting detection indicators for each attack type.
- Design an attack taxonomy by creating a hierarchical classification system with primary attack classes, specific techniques, severity levels, and impact descriptions, and documenting relationships between attack types.
- Create a JSON schema for attack logs, including required and optional fields, and validate the schema against example attacks.
- Implement a logging mechanism that generates conformant log entries, ensures PII scrubbing or pseudonymization, supports asynchronous logging, and enriches context with client and session data.
- Perform integration testing by simulating attacks, verifying log structure conformity, measuring and optimizing performance impact, and validating retention and rotation policies.

## JSON Schema Example

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "LLM Attack Log Entry",
  "type": "object",
  "required": ["timestamp", "event_id", "attack_type", "severity", "detection_source"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 formatted timestamp"
    },
    "event_id": {
      "type": "string",
      "description": "Unique identifier for this event"
    },
    "attack_type": {
      "type": "object",
      "required": ["primary", "technique"],
      "properties": {
        "primary": {
          "type": "string",
          "enum": ["prompt_injection", "jailbreak", "data_extraction", "context_manipulation", "dos", "other"],
          "description": "Primary attack classification"
        },
        "technique": {
          "type": "string",
          "description": "Specific attack technique"
        }
      }
    },
    "severity": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Impact severity of the attack"
    },
    "detection_source": {
      "type": "string",
      "enum": ["yara", "vector_similarity", "token_analysis", "sentiment", "manual", "other"],
      "description": "System component that detected the attack"
    },
    "prompt": {
      "type": "object",
      "properties": {
        "hash": {
          "type": "string",
          "description": "SHA-256 hash of the original prompt"
        },
        "content_excerpt": {
          "type": "string",
          "description": "Sanitized/redacted excerpt of relevant prompt content"
        },
        "tokens": {
          "type": "integer",
          "description": "Number of tokens in the prompt"
        }
      }
    },
    "response": {
      "type": "object",
      "properties": {
        "generated": {
          "type": "boolean",
          "description": "Whether a response was generated or blocked"
        },
        "hash": {
          "type": "string",
          "description": "SHA-256 hash of the response if generated"
        }
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "user_id_hash": {
          "type": "string",
          "description": "Hashed identifier of the user"
        },
        "session_id": {
          "type": "string",
          "description": "Session identifier"
        },
        "client_info": {
          "type": "string",
          "description": "Client application/system information"
        }
      }
    },
    "mitigation": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["allowed", "modified", "blocked", "flagged"],
          "description": "Action taken in response to detected attack"
        },
        "rule_id": {
          "type": "string",
          "description": "Identifier of the rule that triggered the mitigation"
        }
      }
    }
  }
}
```

## Taxonomy Structure

The proposed taxonomy organizes attacks into a hierarchical structure:

1. **Prompt Injection**
   - System Instruction Override
   - Role-Playing Exploitation
   - Hidden Injection (Unicode/invisible characters)
   - Multi-message Manipulation

2. **Jailbreak Techniques**
   - Token Manipulation
   - Context Confusion
   - Hypothetical Scenarios
   - Authority Impersonation
   - DAN (Do Anything Now) variants

3. **Data Extraction**
   - Training Data Leakage
   - System Prompt Extraction
   - User Data Exfiltration
   - Model Parameter Probing

4. **Context Manipulation**
   - RAG Poisoning
   - Context Stuffing
   - History Manipulation

5. **Denial of Service**
   - Token Limit Exhaustion
   - Computational Resource Exhaustion
   - Prompt Complexity Attacks

## Technologies & Resources

- **JSON Schema**: https://json-schema.org/
- **Academic Resources**: 
  - "Taxonomy of Attacks on Machine-Learning Systems" (Kumar et al.)
  - MITRE ATLAS framework for adversarial ML
- **Libraries**: 
  - jsonschema (Python)
  - structlog (Python)
  - FastAPI for schema validation

