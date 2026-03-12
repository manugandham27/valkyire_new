"""
knowledge_base.py
=================
Hybrid knowledge base: local fact store + live Wikidata API fallback.

Verification order:
  1. Local KB (fast, curated, offline)
  2. Wikidata SPARQL API (100M+ facts, free, no key)
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
        use_api: bool = True,
    ):
        self.facts: Dict[Tuple[str, str, str], float] = dict(self.DEFAULT_FACTS)
        self.use_api = use_api
        self._api_available = True  # set to False after first network failure
        if extra_facts:
            self.facts.update(extra_facts)

    # ── Normalisation helper ─────────────────────────────────────────────

    @staticmethod
    def _norm(text: str) -> str:
        """Normalise text for case-insensitive lookup."""
        return text.strip().title()

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
        # Try case-insensitive
        norm_key = (self._norm(claim.subject), claim.relation, self._norm(claim.object))
        if norm_key in self.facts:
            return True, self.facts[norm_key]
        return False, 0.0

    def verify_triple(
        self, subject: str, relation: str, obj: str
    ) -> Tuple[bool, float, str]:
        """
        Hybrid verification: local KB first, then Wikidata API.

        Returns (verified, confidence, source) where source is
        'local', 'wikidata', or ''.
        """
        # ── 1. Local KB ──────────────────────────────────────────────
        # Exact match
        key = (subject, relation, obj)
        if key in self.facts:
            return True, self.facts[key], "local"
        # Normalised match
        norm_key = (self._norm(subject), relation, self._norm(obj))
        if norm_key in self.facts:
            return True, self.facts[norm_key], "local"
        # Relation-agnostic match
        ns, no = self._norm(subject), self._norm(obj)
        for (s, r, o), conf in self.facts.items():
            if self._norm(s) == ns and self._norm(o) == no:
                return True, conf, "local"

        # ── 2. Wikidata API (if enabled) ─────────────────────────────
        if self.use_api and self._api_available:
            try:
                from utils.wikidata_api import verify_claim_wikidata
                verified, conf, desc = verify_claim_wikidata(subject, relation, obj)
                if verified:
                    # Cache into local KB for fast re-queries
                    self.facts[(subject, relation, obj)] = conf
                    return True, conf, "wikidata"
            except Exception:
                self._api_available = False

        return False, 0.0, ""

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
        """
        Return all (relation, object, confidence) entries for *subject*.
        Uses case-insensitive + substring matching so multi-word inputs work.
        """
        ns = self._norm(subject)
        results = []
        for (s, r, o), conf in self.facts.items():
            s_norm = self._norm(s)
            if s_norm == ns or ns in s_norm or s_norm in ns:
                results.append((r, o, conf))
        return results

    def search_by_object(self, obj: str) -> List[Tuple[str, str, float]]:
        """Return all (subject, relation, confidence) entries for *obj*."""
        no = self._norm(obj)
        return [
            (s, r, conf)
            for (s, r, o), conf in self.facts.items()
            if self._norm(o) == no
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
