# Task: Integrate YARA Engine for Prompt Filtering

## Original Requirement

**Title**: Integrate YARA engine for prompt filtering  
**Description**: Add YARA scanning to pre-process all incoming prompts and flag known malicious patterns.  
**Acceptance Criteria**:
* YARA rules executed on every prompt.
* Rule matches logged with prompt ID.

**Labels**: `detection`, `security`, `yara`

## Analysis

YARA is a powerful pattern matching tool widely used in malware analysis and threat hunting. Integrating YARA for LLM prompt filtering will enable us to detect and block known malicious patterns using rule-based matching, complementing our other defense mechanisms with a high-precision filtering layer.

### Key Considerations

1. **Performance Impact**: YARA rules must execute quickly to avoid significantly impacting response times.
2. **Rule Management**: We need a way to organize, version, and deploy rules efficiently.
3. **False Positives**: Rules must be carefully crafted to minimize false positives.
4. **Coverage**: Initial ruleset should cover common attack patterns while being extensible.

### Dependencies

- None directly, but will enhance the "Adversarial Attacks" taxonomy

## Implementation Steps

1. Set up the YARA environment and install required dependencies.
2. Create a directory structure for organizing YARA rules.
3. Configure rule compilation and loading mechanisms.
4. Develop a process for rule management, versioning, and deployment.
5. Create an initial ruleset covering common prompt injection, jailbreaking, data extraction, and evasion patterns.
6. Integrate YARA scanning as a preprocessing step in the prompt input pipeline.
7. Implement caching to avoid rescanning identical prompts.
8. Set up logging for rule matches, including prompt IDs and rule metadata.
9. Optimize scanning performance and benchmark scan times.
10. Implement parallelization and timeouts for scanning if needed.
11. Test the scanner against known attack datasets and measure false positive/negative rates.
12. Tune rules and detection parameters based on test results.
13. Document detection capabilities, limitations, and operational procedures.

## Directory Structure

```
app/
  utils/
    security/
      yara_scanner/
        __init__.py
        scanner.py       # Main scanner module
        rule_compiler.py # Handles rule compilation
        rules/
          injection.yar  # Prompt injection rules
          jailbreak.yar  # Jailbreaking attempt rules
          extraction.yar # Data extraction rules
          evasion.yar    # Rule evasion techniques
```

## Scanner Module Design

```python
# scanner.py

import yara
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class YARAScanner:
    """YARA-based scanner for LLM prompt filtering."""
    
    def __init__(self, rules_dir: Path, cache_size: int = 1000):
        """Initialize the scanner with rules from the specified directory."""
        self.rules = self._compile_rules(rules_dir)
        self.cache = {}  # Simple LRU cache could be added
        self.cache_size = cache_size
        self.cache_hits = 0
        self.total_scans = 0
        
    def _compile_rules(self, rules_dir: Path) -> yara.Rules:
        """Compile all YARA rules in the specified directory."""
        filepaths = {}
        for rule_file in rules_dir.glob("*.yar"):
            filepaths[rule_file.stem] = str(rule_file)
        
        return yara.compile(filepaths=filepaths)
    
    def scan(self, prompt_id: str, prompt_text: str) -> Tuple[bool, List[Dict]]:
        """
        Scan a prompt with YARA rules.
        
        Args:
            prompt_id: Unique identifier for the prompt
            prompt_text: Text content to scan
            
        Returns:
            Tuple of (has_matches, matches)
        """
        self.total_scans += 1
        
        # Check cache first
        prompt_hash = hashlib.md5(prompt_text.encode()).hexdigest()
        if prompt_hash in self.cache:
            self.cache_hits += 1
            return self.cache[prompt_hash]
        
        # Perform scan
        matches = self.rules.match(data=prompt_text)
        result = (len(matches) > 0, [
            {
                "rule": match.rule,
                "namespace": match.namespace,
                "tags": match.tags,
                "meta": match.meta,
                "strings": [
                    {
                        "identifier": s[1],
                        "offset": s[0],
                        # Don't include matched content in logs for privacy
                    } for s in match.strings
                ]
            }
            for match in matches
        ])
        
        # Update cache
        if len(self.cache) >= self.cache_size:
            # Simple FIFO eviction; could be improved to LRU
            self.cache.pop(next(iter(self.cache)))
        self.cache[prompt_hash] = result
        
        # Log matches
        if result[0]:
            for match in result[1]:
                logger.warning(
                    f"YARA match: rule={match['rule']}, prompt_id={prompt_id}, "
                    f"tags={match['tags']}, meta={match['meta']}"
                )
        
        return result
```

## Example YARA Rules

```yara
// injection.yar
rule Prompt_Injection_Basic {
    meta:
        description = "Detects basic prompt injection attempts"
        severity = "medium"
        author = "LLM Audit Assistant Team"
    strings:
        $ignore1 = "ignore previous instructions" nocase
        $ignore2 = "ignore all instructions" nocase
        $ignore3 = "disregard previous" nocase
        $inject1 = "instead, do" nocase
        $inject2 = "from now on you will" nocase
        $inject3 = "you must now" nocase
    condition:
        any of ($ignore*) and any of ($inject*)
}

rule Hidden_Prompt_Injection {
    meta:
        description = "Detects hidden prompt injection using Unicode tricks"
        severity = "high"
        author = "LLM Audit Assistant Team"
    strings:
        // Zero-width characters often used to hide text
        $zwsp = { E2 80 8B }  // Zero-width space
        $zwnj = { E2 80 8C }  // Zero-width non-joiner
        $zwj = { E2 80 8D }   // Zero-width joiner
        
        // Directional formatting often used to hide text
        $rlo = { E2 80 AE }   // Right-to-left override
        $lro = { E2 80 AD }   // Left-to-right override
        
        // Other suspicious patterns
        $base64 = /ignore[a-zA-Z0-9\s]+:[\s]*[a-zA-Z0-9+\/]+={0,2}/
    condition:
        3 of ($zwsp, $zwnj, $zwj, $rlo, $lro) or $base64
}
```

## Integration with API Layer

The YARA scanner should be integrated into the API request flow as a preprocessing step:

```python
# Pseudocode for API integration
from app.utils.security.yara_scanner import YARAScanner
from pathlib import Path

# Initialize scanner once at application startup
scanner = YARAScanner(Path("app/utils/security/yara_scanner/rules"))

@app.before_request
def scan_prompt():
    if request.path == "/api/chat" and request.method == "POST":
        prompt_text = request.json.get("prompt", "")
        prompt_id = request.headers.get("X-Request-ID", "unknown")
        
        has_matches, matches = scanner.scan(prompt_id, prompt_text)
        
        # Store scan results in request context for logging
        request.yara_matches = matches
        
        # Block or flag based on rule severity
        if has_matches and any(m["meta"].get("severity") == "high" for m in matches):
            return jsonify({
                "error": "Request blocked due to security policy violation",
                "code": "SECURITY_POLICY"
            }), 403
```

## Technologies & Resources

- **YARA**: https://github.com/VirusTotal/yara
- **yara-python**: https://github.com/VirusTotal/yara-python
- **References**: 
  - YARA documentation
  - "Detecting Prompt Injection with YARA Rules" (blog article)
  - Security best practices for pattern matching

