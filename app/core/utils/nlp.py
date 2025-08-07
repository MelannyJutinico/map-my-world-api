from transformers import pipeline
from typing import List, Optional


classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_description(description: str, candidate_labels: List[str]) -> Optional[str]:
    """
    Classifies a description into a category using zero-shot classification.
    """
    if not description or not candidate_labels:
        return None

    result = classifier(description, candidate_labels)
    if result and "labels" in result and result["labels"]:
        return result["labels"][0]  
    return None
