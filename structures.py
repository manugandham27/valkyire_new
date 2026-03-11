"""
structures.py
=============
Core data structure representing a verifiable structured claim.

A StructuredClaim is the atomic unit of knowledge in VALKYRIE.
Every sentence the model generates is simultaneously broken down
into (Subject, Relation, Object) triples that can be verified.

Example
-------
  Natural language : "The Eiffel Tower is located in Paris"
  StructuredClaim  : subject="Eiffel Tower", relation="located_in", object="Paris"
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StructuredClaim:
    """
    Represents one verifiable fact as a (subject, relation, object) triple.

    Attributes
    ----------
    subject    : The entity the claim is about.
    relation   : The relationship type (e.g., 'located_in', 'founded_by').
    object     : The value or entity the subject relates to.
    confidence : How confident the model is about this claim (0.0 – 1.0).
    verified   : Whether the claim passed Knowledge Base verification.
    layer      : Which decoder layer produced this claim.
    """

    subject    : str
    relation   : str
    object     : str
    confidence : float
    verified   : bool  = False
    layer      : int   = -1

    # ── Natural language templates ─────────────────────────────────────
    _TEMPLATES: dict = field(default_factory=lambda: {
        "located_in"    : lambda s, o: f"{s} is located in {o}",
        "capital_of"    : lambda s, o: f"{s} is the capital of {o}",
        "founded_by"    : lambda s, o: f"{s} was founded by {o}",
        "population_of" : lambda s, o: f"{s} has a population of {o}",
        "discovered"    : lambda s, o: f"{s} discovered {o}",
        "color"         : lambda s, o: f"{s} is {o} in color",
    }, repr=False)

    def to_text(self) -> str:
        """Convert the triple into a human-readable sentence."""
        fn = self._TEMPLATES.get(self.relation)
        if fn:
            return fn(self.subject, self.object)
        return f"{self.subject} {self.relation} {self.object}"

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary (useful for logging)."""
        return {
            "subject"    : self.subject,
            "relation"   : self.relation,
            "object"     : self.object,
            "confidence" : round(self.confidence, 4),
            "verified"   : self.verified,
            "layer"      : self.layer,
            "text"       : self.to_text(),
        }

    def __repr__(self) -> str:
        status = "VERIFIED" if self.verified else "UNVERIFIED"
        return (
            f"Claim({self.subject!r} --[{self.relation}]--> {self.object!r} | "
            f"conf={self.confidence:.2f} | {status} | layer={self.layer})"
        )
