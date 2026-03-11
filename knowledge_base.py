"""
knowledge_base.py
=================
Simulated knowledge base that stores (subject, relation, object) facts
with confidence scores and supports structured claim verification.

In a production system this would be replaced by a real KB such as
Wikidata, a vector database, or a retrieval-augmented store.
"""

from typing import Dict, List, Optional, Tuple
from models.structures import StructuredClaim


class KnowledgeBase:
    """
    Stores ground-truth facts and verifies StructuredClaims against them.

    Each fact is a (subject, relation, object) triple mapped to a
    confidence score in [0, 1] representing how reliable that fact is.

    Parameters
    ----------
    extra_facts : optional additional facts to merge in at construction.
    """

    # ── Built-in seed facts ────────────────────────────────────────────
    DEFAULT_FACTS: Dict[Tuple[str, str, str], float] = {
        ("Eiffel Tower", "located_in",    "Paris")      : 1.00,
        ("Paris",        "capital_of",    "France")      : 1.00,
        ("Apple",        "founded_by",    "Steve Jobs")  : 1.00,
        ("Microsoft",    "founded_by",    "Bill Gates")  : 1.00,
        ("Google",       "founded_by",    "Larry Page")  : 1.00,
        ("Tokyo",        "capital_of",    "Japan")       : 1.00,
        ("Tokyo",        "population_of", "37 million")  : 0.95,
        ("London",       "capital_of",    "England")     : 1.00,
        ("London",       "population_of", "9 million")   : 0.98,
        ("Einstein",     "discovered",    "Relativity")  : 1.00,
        ("Mars",         "color",         "Red")         : 1.00,
        ("Amazon",       "founded_by",    "Jeff Bezos")  : 1.00,
        ("Tesla",        "founded_by",    "Elon Musk")   : 0.90,
        ("Berlin",       "capital_of",    "Germany")     : 1.00,
        ("Rome",         "capital_of",    "Italy")       : 1.00,
    }

    def __init__(
        self,
        extra_facts: Optional[Dict[Tuple[str, str, str], float]] = None,
    ):
        self.facts: Dict[Tuple[str, str, str], float] = dict(self.DEFAULT_FACTS)
        if extra_facts:
            self.facts.update(extra_facts)

    # ── Core verification ──────────────────────────────────────────────

    def verify_claim(self, claim: StructuredClaim) -> Tuple[bool, float]:
        """
        Check whether *claim* exists in the knowledge base.

        Returns
        -------
        (is_known, confidence)
        """
        key = (claim.subject, claim.relation, claim.object)
        if key in self.facts:
            return True, self.facts[key]
        return False, 0.0

    def verify_triple(
        self, subject: str, relation: str, obj: str
    ) -> Tuple[bool, float]:
        """Convenience wrapper that accepts raw strings."""
        key = (subject, relation, obj)
        if key in self.facts:
            return True, self.facts[key]
        return False, 0.0

    # ── Management ────────────────────────────────────────────────────

    def add_fact(
        self,
        subject: str,
        relation: str,
        obj: str,
        confidence: float = 1.0,
    ) -> None:
        """Dynamically add a new fact."""
        self.facts[(subject, relation, obj)] = min(max(confidence, 0.0), 1.0)

    def remove_fact(self, subject: str, relation: str, obj: str) -> bool:
        """Remove a fact if present. Returns True if it existed."""
        key = (subject, relation, obj)
        if key in self.facts:
            del self.facts[key]
            return True
        return False

    def search_subject(self, subject: str) -> List[Tuple[str, str, float]]:
        """Return all (relation, object, confidence) entries for *subject*."""
        return [
            (r, o, conf)
            for (s, r, o), conf in self.facts.items()
            if s == subject
        ]

    def summary(self) -> str:
        lines = [f"KnowledgeBase ({len(self.facts)} facts):"]
        for (s, r, o), conf in self.facts.items():
            lines.append(f"  ({s}) --[{r}]--> ({o})  conf={conf:.2f}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.facts)

    def __repr__(self) -> str:
        return f"KnowledgeBase({len(self.facts)} facts)"
