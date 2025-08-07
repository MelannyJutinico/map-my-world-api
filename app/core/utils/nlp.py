"""
Utility module for automatic category classification using zero-shot NLP.

This module provides a function to infer the most relevant category for a given
textual description, based on a list of candidate labels, using the
facebook/bart-large-mnli model from Hugging Face.
"""

from transformers import pipeline
from typing import List, Optional

# Initialize the zero-shot classification pipeline once at module load time
classifier = pipeline(
    task="zero-shot-classification",
    model="facebook/bart-large-mnli"
)

def classify_description(
    description: str,
    candidate_labels: List[str]
) -> Optional[str]:
    """
    Infer the most likely category label for a description using zero-shot classification.

    Given a free-text description and a list of possible category labels, this function
    returns the label with the highest confidence score, or None if no labels are provided
    or the classification fails.

    :param description: A text snippet describing the location or item to classify.
    :param candidate_labels: A list of category names to evaluate against the description.
    :return: The label with the highest predicted relevance, or None on error or empty input.
    """
    if not description or not candidate_labels:
        return None

    result = classifier(description, candidate_labels)
    labels = result.get("labels") if isinstance(result, dict) else None
    if labels:
        return labels[0]
    return None
