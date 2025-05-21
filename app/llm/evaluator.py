# Metrics, eval datasets

from typing import List, Dict

import evaluate
# Placeholder for evaluation metrics and datasets
import yaml

bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")


# Load Q&A pairs from YAML/JSON
def load_eval_dataset(path: str) -> List[Dict]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def evaluate_qa(predictions: List[str], references: List[str]) -> Dict[str, float]:
    bleu_result = bleu.compute(predictions=predictions, references=[[r] for r in references])
    bleu_score = bleu_result["bleu"] if bleu_result and "bleu" in bleu_result else 0.0
    rouge_result = rouge.compute(predictions=predictions, references=references)
    rouge_score = rouge_result["rougeL"] if rouge_result and "rougeL" in rouge_result else 0.0
    # Placeholder for embedding similarity
    semantic = 0.0
    return {"bleu": bleu_score, "rouge": rouge_score, "semantic": semantic}

# Add more evaluation utilities as needed
