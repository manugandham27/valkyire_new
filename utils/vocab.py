"""
vocab.py
========
Vocabulary helpers for the VALKYRIE-Decoder.

For production use, replace create_demo_vocabulary() with a real
tokeniser such as tiktoken, SentencePiece, or HuggingFace tokenisers.
"""

from typing import Dict


def create_demo_vocabulary() -> Dict[str, Dict]:
    """
    Build a demo word ↔ index mapping that covers the KB facts
    and common function words.
    """
    tokens = [
        # Special tokens
        "<PAD>", "<SOS>", "<EOS>", "<UNK>",
        # Function words
        "the", "is", "in", "of", "was", "by", "a", "an", "and",
        "has", "are", "have", "it", "its", "be", "been",
        # Named entities (aligned with KnowledgeBase)
        "Eiffel", "Tower", "Paris", "France", "capital",
        "Apple", "founded", "Steve", "Jobs", "Microsoft",
        "Bill", "Gates", "Tokyo", "Japan", "London", "England",
        "Einstein", "Relativity", "Mars", "Amazon", "Jeff",
        "Bezos", "Tesla", "Elon", "Musk", "Google", "Larry",
        "Page", "Berlin", "Germany", "Rome", "Italy",
        # Relations as words
        "located", "capital", "population", "million",
        "discovered", "red", "color",
    ]
    word_to_idx = {w: i for i, w in enumerate(tokens)}
    idx_to_word = {i: w for i, w in enumerate(tokens)}
    return {"word_to_idx": word_to_idx, "idx_to_word": idx_to_word}


def vocab_size(vocabulary: Dict[str, Dict]) -> int:
    return len(vocabulary["word_to_idx"])


def encode(text: str, vocabulary: Dict[str, Dict]) -> list:
    """Simple whitespace tokeniser. Unknown words → <UNK> index."""
    unk = vocabulary["word_to_idx"].get("<UNK>", 3)
    return [vocabulary["word_to_idx"].get(w, unk) for w in text.split()]


def decode(indices: list, vocabulary: Dict[str, Dict]) -> str:
    return " ".join(vocabulary["idx_to_word"].get(i, "<UNK>") for i in indices)
