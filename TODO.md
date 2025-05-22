# TODO

### 🔐 **Adversarial Machine Learning**

**Title**: Integrate adversarial prompt testing in CI/CD
**Description**:
Add automated adversarial prompt testing (e.g., using TextAttack or custom fuzzers) to the CI/CD pipeline to simulate AML threats.
**Acceptance Criteria**:

* Integration of at least one adversarial prompt generator.
* Report generated during each CI run.
* Fail pipeline on high-risk outputs.
  **Labels**: `security`, `adversarial`, `mlops`

---

### 🎯 **Adversarial Attacks**

**Title**: Create taxonomy and log structure for prompt-based attacks
**Description**:
Develop a schema for logging and classifying detected adversarial attacks (e.g., evasion, prompt injection, context abuse).
**Acceptance Criteria**:

* JSON schema for attack events.
* Logged entries with timestamps, prompt content, severity.
  **Labels**: `security`, `logging`, `threat-model`

---

### 🕵️‍♂️ **YARA Scanner**

**Title**: Integrate YARA engine for prompt filtering
**Description**:
Add YARA scanning to pre-process all incoming prompts and flag known malicious patterns.
**Acceptance Criteria**:

* YARA rules executed on every prompt.
* Rule matches logged with prompt ID.
  **Labels**: `detection`, `security`, `yara`

---

### 💉 **Prompt Injection**

**Title**: Harden prompt templates against injection
**Description**:
Refactor system prompts to isolate user inputs via strict delimiters and token encoding to mitigate injection.
**Acceptance Criteria**:

* Updated prompt format with isolation.
* Injection tests pass.
  **Labels**: `prompt-injection`, `hardening`

---

### 🧠 **Large Language Models**

**Title**: Implement context length truncation and token inspection
**Description**:
Enforce safe max context limits and inspect token length and entropy to detect unusual input patterns.
**Acceptance Criteria**:

* Max context token check with fallback.
* Logging of token entropy for analysis.
  **Labels**: `llm`, `security`, `tokenization`

---

### 🛡️ **LLMOps**

**Title**: Deploy logging and replay pipeline for LLM interactions
**Description**:
Implement comprehensive logging (prompt, response, metadata) with ability to replay LLM sessions for audit/review.
**Acceptance Criteria**:

* Log format standardized.
* Replay tool available in dev environment.
  **Labels**: `ops`, `audit`, `llmops`

---

### 📚 **Vector Database / Similarity**

**Title**: Integrate vector DB for prompt similarity search
**Description**:
Store all prompts in a vector DB (e.g., FAISS, Qdrant) and implement semantic similarity checks for detecting near-duplicate attacks.
**Acceptance Criteria**:

* Vector DB integration complete.
* API available to query similar prompts.
* Threshold-based alerting.
  **Labels**: `vector-db`, `similarity`, `retrieval`

---

### 🔁 **Auto-Updating on Detected Prompts**

**Title**: Automate rule/policy updates from flagged prompts
**Description**:
When a prompt triggers a detection rule (e.g., YARA), automatically update filters or rulesets to block similar inputs.
**Acceptance Criteria**:

* Detection → rule update pipeline implemented.
* Manual approval flow for high-risk changes.
  **Labels**: `automation`, `security`, `devops`

---

### ⚙️ **Heuristics via YARA**

**Title**: Develop rule severity tagging for YARA hits
**Description**:
Assign severity levels to YARA rules to enable tiered mitigation (warn/block/escalate).
**Acceptance Criteria**:

* Rules tagged with severity metadata.
* Log entries reflect rule severity.
  **Labels**: `yara`, `rules`, `threat-detection`

---

### 🔄 **Transformer Model Monitoring**

**Title**: Add token pattern anomaly detector for transformer output
**Description**:
Detect anomalous generation behavior (repetition, echoing, irrelevant tokens) in transformer output streams.
**Acceptance Criteria**:

* Anomaly detector logs flagged outputs.
* Configurable thresholds and alerts.
  **Labels**: `transformer`, `output-analysis`, `anomaly-detection`

---

### 🔍 **Prompt-Response Similarity**

**Title**: Implement prompt-response similarity scoring
**Description**:
Compute cosine similarity between prompt and response embeddings to detect prompt leakage or excessive influence.
**Acceptance Criteria**:

* Embedding model integrated.
* Scores logged and threshold-tuned.
  **Labels**: `similarity`, `response-analysis`, `leakage-detection`

---

### 🧪 **Canary Tokens**

**Title**: Deploy canary tokens to detect LLM output leaks
**Description**:
Embed identifiable canary strings into system prompts or training data to detect model exfiltration.
**Acceptance Criteria**:

* Canary tokens inserted.
* Monitoring in place for response leaks.
  **Labels**: `canary`, `monitoring`, `llm-leakage`

---

### 🧠 **Sentiment Analysis**

**Title**: Add sentiment analysis filter to input pipeline
**Description**:
Use a sentiment classifier to detect toxic, aggressive, or manipulative prompt tone.
**Acceptance Criteria**:

* Toxicity score calculated for every prompt.
* Routing or alerting for extreme values.
  **Labels**: `nlp`, `filtering`, `sentiment-analysis`

---

### 📏 **Relevance via LiteLLM**

**Title**: Integrate relevance scoring via LiteLLM
**Description**:
Score each prompt-response pair for relevance using LiteLLM to filter or reroute irrelevant chains.
**Acceptance Criteria**:

* LiteLLM scoring functional.
* Irrelevant prompts flagged or dropped.
  **Labels**: `relevance`, `liteLLM`, `response-quality`

---

### 🔄 **Paraphrasing Detection**

**Title**: Detect paraphrased variants of known prompt attacks
**Description**:
Use paraphrase detection to flag semantically similar adversarial prompts that evade regex/YARA.
**Acceptance Criteria**:

* Embedding or paraphrase model integrated.
* Paraphrased variants matched against blacklist.
  **Labels**: `paraphrasing`, `evasion`, `detection`

