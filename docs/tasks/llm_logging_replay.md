# Task: Deploy Logging and Replay Pipeline for LLM Interactions

## Original Requirement

**Title**: Deploy logging and replay pipeline for LLM interactions  
**Description**: Implement comprehensive logging (prompt, response, metadata) with ability to replay LLM sessions for audit/review.  
**Acceptance Criteria**:
* Log format standardized.
* Replay tool available in dev environment.

**Labels**: `ops`, `audit`, `llmops`

## Analysis

This task focuses on creating a robust logging system for LLM interactions that captures detailed information about each interaction and provides a way to replay those interactions for debugging, auditing, and quality improvement. This capability is critical for compliance, security monitoring, and continuous improvement of the LLM Audit Assistant.

### Key Considerations

1. **Privacy and Compliance**: Logs must comply with data protection regulations and internal privacy policies.
2. **Performance Impact**: Logging should have minimal impact on response times.
3. **Storage Requirements**: High-volume logging requires efficient storage solutions.
4. **Replay Fidelity**: Replayed sessions should accurately recreate the original interaction.

### Dependencies

- Existing logging infrastructure (Loki, based on the docker-compose file)
- Access to LLM client implementation
- Storage solution for log data

## Implementation Steps

- Design a comprehensive log schema for LLM interactions, including fields for request/response content, metadata, and timestamps, and validate the schema with security and compliance teams.
- Implement a logging module for LLM interactions, add hooks in the LLM client and API routes, support asynchronous logging, and provide configuration options for log levels and PII handling.
- Integrate with persistent storage, implement retention policies and data lifecycle management, create indexes for efficient querying, and set up backup procedures.
- Develop a replay tool for LLM sessions, including CLI and web interface capabilities for browsing, searching, and modifying prompts, and comparing original and replayed responses.
- Test the logging and replay system at scale, verify replay accuracy, create documentation and usage examples, and provide guidelines for log analysis.

## Log Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "LLM Interaction Log",
  "type": "object",
  "required": ["interaction_id", "timestamp", "user_id", "session_id", "request", "response"],
  "properties": {
    "interaction_id": {
      "type": "string",
      "description": "Unique identifier for this interaction"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 formatted timestamp"
    },
    "user_id": {
      "type": "string",
      "description": "ID of the user (hashed if PII protection enabled)"
    },
    "session_id": {
      "type": "string",
      "description": "Session identifier for grouping interactions"
    },
    "request": {
      "type": "object",
      "properties": {
        "prompt": {
          "type": "string",
          "description": "User prompt text"
        },
        "system_prompt": {
          "type": "string",
          "description": "System instructions provided to the model"
        },
        "context": {
          "type": "array",
          "description": "Context documents provided to the model",
          "items": {
            "type": "object",
            "properties": {
              "content": {
                "type": "string"
              },
              "source": {
                "type": "string"
              },
              "metadata": {
                "type": "object"
              }
            }
          }
        },
        "parameters": {
          "type": "object",
          "description": "Model parameters (temperature, etc.)"
        }
      }
    },
    "response": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string",
          "description": "Model response text"
        },
        "completion_tokens": {
          "type": "integer",
          "description": "Number of tokens in the response"
        },
        "finish_reason": {
          "type": "string",
          "description": "Reason the model stopped generating (e.g., 'stop', 'length')"
        }
      }
    },
    "metrics": {
      "type": "object",
      "properties": {
        "prompt_tokens": {
          "type": "integer"
        },
        "total_tokens": {
          "type": "integer"
        },
        "latency_ms": {
          "type": "integer"
        },
        "embedding_time_ms": {
          "type": "integer"
        },
        "retrieval_time_ms": {
          "type": "integer"
        },
        "llm_time_ms": {
          "type": "integer"
        }
      }
    },
    "evaluation": {
      "type": "object",
      "properties": {
        "relevance_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "quality_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "security_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "flagged": {
          "type": "boolean"
        },
        "flag_reason": {
          "type": "string"
        }
      }
    },
    "security": {
      "type": "object",
      "properties": {
        "prompt_entropy": {
          "type": "number"
        },
        "yara_matches": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "token_inspection_result": {
          "type": "object"
        },
        "sensitivity_level": {
          "type": "string",
          "enum": ["public", "internal", "confidential", "restricted"]
        }
      }
    }
  }
}
```

## Logging Module Implementation

```python
# app/utils/logging/llm_logger.py

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient

class LLMInteractionLogger:
    """Logger for LLM interactions with storage and replay capabilities."""
    
    def __init__(self, db_uri: Optional[str] = None, async_logging: bool = True):
        """
        Initialize the LLM interaction logger.
        
        Args:
            db_uri: MongoDB connection string (falls back to env var)
            async_logging: Whether to log asynchronously
        """
        self.logger = logging.getLogger("llm_interactions")
        self.async_logging = async_logging
        
        # Connect to MongoDB for persistent storage
        mongo_uri = db_uri or os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.llm_audit_assistant
        self.interactions = self.db.interactions
        
        # Create indexes for efficient querying
        asyncio.create_task(self._create_indexes())
    
    async def _create_indexes(self):
        """Create indexes on commonly queried fields."""
        await self.interactions.create_index("timestamp")
        await self.interactions.create_index("interaction_id")
        await self.interactions.create_index("user_id")
        await self.interactions.create_index("session_id")
        await self.interactions.create_index([("request.prompt", "text")])
    
    async def log_interaction(self, 
                             user_id: str,
                             session_id: str,
                             prompt: str,
                             system_prompt: str,
                             context: List[Dict[str, Any]],
                             parameters: Dict[str, Any],
                             response: str,
                             metrics: Dict[str, Any],
                             evaluation: Optional[Dict[str, Any]] = None,
                             security: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an LLM interaction.
        
        Returns:
            interaction_id: The ID of the logged interaction
        """
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Create log entry
        log_entry = {
            "interaction_id": interaction_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "session_id": session_id,
            "request": {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "context": context,
                "parameters": parameters
            },
            "response": {
                "content": response,
                "completion_tokens": metrics.get("completion_tokens"),
                "finish_reason": metrics.get("finish_reason")
            },
            "metrics": metrics
        }
        
        # Add optional fields if provided
        if evaluation:
            log_entry["evaluation"] = evaluation
        if security:
            log_entry["security"] = security
        
        # Log to standard logger (might go to Loki)
        self.logger.info(
            f"LLM Interaction: id={interaction_id} user={user_id} "
            f"tokens={metrics.get('total_tokens')} latency={metrics.get('latency_ms')}ms"
        )
        
        # Store in database
        if self.async_logging:
            # Don't block the request
            asyncio.create_task(self._store_log(log_entry))
        else:
            # Blocking store for critical logs
            await self._store_log(log_entry)
        
        return interaction_id
    
    async def _store_log(self, log_entry: Dict[str, Any]) -> None:
        """Store a log entry in the database."""
        try:
            await self.interactions.insert_one(log_entry)
        except Exception as e:
            self.logger.error(f"Failed to store LLM interaction log: {e}")
    
    async def get_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific interaction by ID."""
        return await self.interactions.find_one({"interaction_id": interaction_id})
    
    async def get_session_interactions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all interactions for a session."""
        cursor = self.interactions.find({"session_id": session_id})
        return await cursor.to_list(length=None)
    
    async def search_interactions(self, 
                                query: Optional[str] = None,
                                user_id: Optional[str] = None,
                                time_range: Optional[Dict[str, str]] = None,
                                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for interactions based on criteria.
        
        Args:
            query: Free text search in prompt and response
            user_id: Filter by user
            time_range: Dict with 'start' and 'end' in ISO format
            limit: Maximum number of results
            
        Returns:
            List of matching interaction logs
        """
        filter_dict = {}
        
        if query:
            filter_dict["$text"] = {"$search": query}
        
        if user_id:
            filter_dict["user_id"] = user_id
        
        if time_range:
            time_filter = {}
            if "start" in time_range:
                time_filter["$gte"] = time_range["start"]
            if "end" in time_range:
                time_filter["$lte"] = time_range["end"]
            if time_filter:
                filter_dict["timestamp"] = time_filter
        
        cursor = self.interactions.find(filter_dict).limit(limit)
        return await cursor.to_list(length=limit)
```

## Replay Tool Implementation

```python
# app/utils/replay/replayer.py

import asyncio
import json
from typing import Dict, List, Any, Optional
import argparse
import sys
from app.llm.client import LLMClient
from app.utils.logging.llm_logger import LLMInteractionLogger

class LLMInteractionReplayer:
    """Tool for replaying LLM interactions from logs."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, logger: Optional[LLMInteractionLogger] = None):
        """
        Initialize the replayer.
        
        Args:
            llm_client: LLM client for sending requests
            logger: Logger instance for accessing logs
        """
        self.llm_client = llm_client or LLMClient()
        self.logger = logger or LLMInteractionLogger()
    
    async def replay_interaction(self, 
                               interaction_id: str, 
                               modify_prompt: Optional[str] = None,
                               modify_system: Optional[str] = None,
                               modify_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Replay a specific interaction, optionally with modifications.
        
        Args:
            interaction_id: ID of the interaction to replay
            modify_prompt: New prompt to use instead of the original
            modify_system: New system prompt to use
            modify_params: Parameter overrides
            
        Returns:
            Dict with original and replayed responses and comparison metrics
        """
        # Get the original interaction
        interaction = await self.logger.get_interaction(interaction_id)
        if not interaction:
            raise ValueError(f"Interaction {interaction_id} not found")
        
        # Extract request components
        original_prompt = interaction["request"]["prompt"]
        original_system = interaction["request"]["system_prompt"]
        original_context = interaction["request"]["context"]
        original_params = interaction["request"]["parameters"]
        
        # Apply modifications if provided
        prompt = modify_prompt or original_prompt
        system = modify_system or original_system
        params = {**original_params, **(modify_params or {})}
        
        # Send replay request
        start_time = asyncio.get_event_loop().time()
        replay_response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=system,
            context=original_context,
            **params
        )
        end_time = asyncio.get_event_loop().time()
        
        # Calculate metrics
        latency_ms = int((end_time - start_time) * 1000)
        prompt_similarity = self._calculate_similarity(original_prompt, prompt)
        response_similarity = self._calculate_similarity(
            interaction["response"]["content"], 
            replay_response["content"]
        )
        
        # Create result object
        result = {
            "original": {
                "prompt": original_prompt,
                "system_prompt": original_system,
                "parameters": original_params,
                "response": interaction["response"]["content"]
            },
            "replay": {
                "prompt": prompt,
                "system_prompt": system,
                "parameters": params,
                "response": replay_response["content"],
                "latency_ms": latency_ms
            },
            "comparison": {
                "prompt_similarity": prompt_similarity,
                "response_similarity": response_similarity,
                "prompt_modified": original_prompt != prompt,
                "system_modified": original_system != system,
                "params_modified": original_params != params
            }
        }
        
        return result
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Simple implementation - this could be replaced with embedding similarity
        or other more sophisticated measures.
        """
        # This is a very basic similarity measure
        # In a real implementation, use embeddings or more sophisticated NLP
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

# CLI interface for the replayer
async def main():
    parser = argparse.ArgumentParser(description="Replay LLM interactions from logs")
    parser.add_argument("interaction_id", help="ID of the interaction to replay")
    parser.add_argument("--prompt", help="Override the original prompt")
    parser.add_argument("--system", help="Override the system prompt")
    parser.add_argument("--temp", type=float, help="Override temperature parameter")
    
    args = parser.parse_args()
    
    # Set up parameter overrides
    param_overrides = {}
    if args.temp is not None:
        param_overrides["temperature"] = args.temp
    
    # Create replayer and execute
    replayer = LLMInteractionReplayer()
    result = await replayer.replay_interaction(
        args.interaction_id,
        modify_prompt=args.prompt,
        modify_system=args.system,
        modify_params=param_overrides
    )
    
    # Print results
    print("\n=== ORIGINAL INTERACTION ===")
    print(f"Prompt: {result['original']['prompt'][:100]}...")
    print(f"Response: {result['original']['response'][:100]}...")
    
    print("\n=== REPLAYED INTERACTION ===")
    print(f"Prompt: {result['replay']['prompt'][:100]}...")
    print(f"Response: {result['replay']['response'][:100]}...")
    
    print("\n=== COMPARISON ===")
    print(f"Response similarity: {result['comparison']['response_similarity']:.2f}")
    print(f"Latency: {result['replay']['latency_ms']}ms")
    
    # Write full result to file for detailed review
    with open(f"replay_{args.interaction_id}.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nFull result written to replay_{args.interaction_id}.json")

if __name__ == "__main__":
    asyncio.run(main())
```

## Web Interface Integration

Add a simple web interface to the existing UI for browsing logs and replaying interactions:

```python
# ui/pages/interaction_logs.py

import streamlit as st
import pandas as pd
import requests
import json
import datetime

st.title("LLM Interaction Logs")

# Filters
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start date", datetime.date.today() - datetime.timedelta(days=7))
end_date = st.sidebar.date_input("End date", datetime.date.today())
user_filter = st.sidebar.text_input("User ID (optional)")
search_query = st.sidebar.text_input("Search terms (optional)")

# Convert to ISO format
start_datetime = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + "Z"
end_datetime = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + "Z"

# Search parameters
params = {
    "time_range": {
        "start": start_datetime,
        "end": end_datetime
    },
    "limit": 100
}

if user_filter:
    params["user_id"] = user_filter
if search_query:
    params["query"] = search_query

# API call
response = requests.post(
    f"{st.session_state.api_url}/api/logs/search",
    json=params,
    headers={"Authorization": f"Bearer {st.session_state.token}"}
)

if response.status_code == 200:
    logs = response.json()
    
    # Display as table
    if logs:
        # Convert to DataFrame for better display
        df = pd.DataFrame([
            {
                "Time": log["timestamp"],
                "User": log["user_id"],
                "Prompt": log["request"]["prompt"][:50] + "..." if len(log["request"]["prompt"]) > 50 else log["request"]["prompt"],
                "Tokens": log["metrics"]["total_tokens"],
                "Latency": f"{log['metrics']['latency_ms']}ms",
                "ID": log["interaction_id"]
            }
            for log in logs
        ])
        
        st.dataframe(df)
        
        # Select interaction for details
        selected_id = st.selectbox("Select interaction for details", df["ID"].tolist())
        
        if selected_id:
            selected_log = next((log for log in logs if log["interaction_id"] == selected_id), None)
            
            if selected_log:
                st.header("Interaction Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Request")
                    st.text_area("Prompt", selected_log["request"]["prompt"], height=200)
                    st.text_area("System Prompt", selected_log["request"]["system_prompt"], height=100)
                    
                    # Display parameters
                    st.json(selected_log["request"]["parameters"])
                
                with col2:
                    st.subheader("Response")
                    st.text_area("Content", selected_log["response"]["content"], height=300)
                    
                    # Display metrics
                    st.json(selected_log["metrics"])
                
                # Replay section
                st.header("Replay Interaction")
                
                with st.form("replay_form"):
                    modified_prompt = st.text_area("Modified prompt (leave empty to use original)", "", height=100)
                    temperature = st.slider("Temperature", 0.0, 1.0, float(selected_log["request"]["parameters"].get("temperature", 0.7)))
                    
                    replay_button = st.form_submit_button("Replay Interaction")
                    
                    if replay_button:
                        # Prepare replay request
                        replay_params = {
                            "interaction_id": selected_id
                        }
                        
                        if modified_prompt:
                            replay_params["modify_prompt"] = modified_prompt
                        
                        if temperature != float(selected_log["request"]["parameters"].get("temperature", 0.7)):
                            replay_params["modify_params"] = {"temperature": temperature}
                        
                        # Send replay request
                        replay_response = requests.post(
                            f"{st.session_state.api_url}/api/logs/replay",
                            json=replay_params,
                            headers={"Authorization": f"Bearer {st.session_state.token}"}
                        )
                        
                        if replay_response.status_code == 200:
                            result = replay_response.json()
                            
                            st.subheader("Original Response")
                            st.text_area("", result["original"]["response"], height=200)
                            
                            st.subheader("Replayed Response")
                            st.text_area("", result["replay"]["response"], height=200)
                            
                            st.metric("Response Similarity", f"{result['comparison']['response_similarity']:.2f}")
                            st.metric("Replay Latency", f"{result['replay']['latency_ms']}ms")
                        else:
                            st.error(f"Error replaying interaction: {replay_response.text}")
    else:
        st.info("No interactions found matching the criteria.")
else:
    st.error(f"Error retrieving logs: {response.text}")
```

## Technologies & Resources

- **Database**: MongoDB for log storage
- **Libraries**: AsyncIO for non-blocking operations, Pandas for data manipulation
- **UI**: Streamlit for the web interface
- **References**: 
  - "LLM observability best practices" (papers/blogs)
  - "Privacy-preserving logging for ML" (research)

## Estimated Effort

- **Skill Requirements**: Python, Async programming, Database knowledge, UI development
