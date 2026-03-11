"""
conflict_detector.py
====================
NOVELTY #3 — Claim Conflict Detection & Suppression

What problem does this solve?
------------------------------
Imagine the model generates two claims in the same pass:
  Claim 1: "Apple was founded by Steve Jobs"
  Claim 2: "Apple was founded by Bill Gates"

Both might individually have decent confidence scores and pass
KB verification independently. But together they CONTRADICT each other.
Without conflict detection, BOTH could reach the output, producing
an incoherent response.

This is the first model to catch such contradictions INSIDE the
decoder loop, before they reach the output.

Three Conflict Types Detected
------------------------------
TYPE 1 — OBJECT CONFLICT
  Same subject + same relation, but different objects.
  Example: "Apple founded_by Steve Jobs" vs "Apple founded_by Bill Gates"
  → Both suppressed

TYPE 2 — RELATION CONFLICT
  Same subject + same object, but mutually exclusive relations.
  Example: "Paris capital_of France" vs "Paris located_in France"
  → Both suppressed (a city can't be both capital AND merely located)

TYPE 3 — SYMMETRIC CONFLICT
  A --rel--> B  and  B --rel--> A  simultaneously asserted,
  for relations that are inherently asymmetric (capital_of, founded_by).
  Example: "France capital_of Paris" vs "Paris capital_of France"
  → Both suppressed

Detection Strategy
-------------------
Hybrid approach:
  1. Rule-based layer   – fast, deterministic, catches known conflict patterns
  2. Learned MLP layer  – catches soft/ambiguous conflicts via embeddings

Final conflict score = max(rule_score, learned_score)
If score >= conflict_threshold → both claims in the pair are suppressed
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple

from models.structures import StructuredClaim


# Relations that are asymmetric (A→B does NOT imply B→A)
ASYMMETRIC_RELATIONS = frozenset({
    "capital_of", "founded_by", "located_in",
    "parent_of",  "discovered", "invented_by",
})

# Pairs of relations that are mutually exclusive for the same (subj, obj)
EXCLUSIVE_RELATION_PAIRS = [
    frozenset({"capital_of", "located_in"}),
    frozenset({"founded_by", "invented_by"}),
]


class ClaimEmbedder(nn.Module):
    """
    Embeds a StructuredClaim into a fixed-size vector.
    Uses learned lookup tables for subjects, relations, and objects.
    Concatenates the three embeddings and projects to embed_dim.

    Parameters
    ----------
    embed_dim : output embedding dimension.
    """

    # Vocabulary lists (extended for the richer KB)
    SUBJECTS = [
        "Eiffel Tower", "Paris", "Apple", "Tokyo", "Mars",
        "Microsoft", "London", "Einstein", "Amazon", "Tesla",
        "Google", "Berlin", "Rome", "France", "Japan",
        "UNKNOWN",
    ]
    RELATIONS = [
        "located_in", "capital_of", "founded_by", "population_of",
        "discovered", "color", "invented_by", "parent_of",
        "UNKNOWN",
    ]
    OBJECTS = [
        "Paris", "France", "Steve Jobs", "37 million", "Red",
        "Bill Gates", "9 million", "Relativity", "Jeff Bezos",
        "Elon Musk", "Larry Page", "Germany", "Italy",
        "Japan", "England", "UNKNOWN",
    ]

    def __init__(self, embed_dim: int = 64):
        super().__init__()
        self.embed_dim = embed_dim
        self.subj_emb  = nn.Embedding(len(self.SUBJECTS),  embed_dim)
        self.rel_emb   = nn.Embedding(len(self.RELATIONS), embed_dim)
        self.obj_emb   = nn.Embedding(len(self.OBJECTS),   embed_dim)
        self.proj      = nn.Linear(embed_dim * 3, embed_dim)

    def _idx(self, value: str, vocab: List[str]) -> int:
        try:
            return vocab.index(value)
        except ValueError:
            return len(vocab) - 1   # → UNKNOWN

    def embed(self, claim: StructuredClaim) -> torch.Tensor:
        """Return a (1, embed_dim) embedding for *claim*."""
        s = torch.tensor([self._idx(claim.subject,  self.SUBJECTS)])
        r = torch.tensor([self._idx(claim.relation, self.RELATIONS)])
        o = torch.tensor([self._idx(claim.object,   self.OBJECTS)])
        combined = torch.cat([self.subj_emb(s), self.rel_emb(r), self.obj_emb(o)], dim=-1)
        return self.proj(combined)   # (1, embed_dim)


class ConflictDetector(nn.Module):
    """
    Scans all pairs of generated claims for logical contradictions.
    Suppresses BOTH claims in any conflicting pair.

    Parameters
    ----------
    embed_dim          : claim embedding dimension.
    conflict_threshold : minimum score to flag a pair as conflicting.
    """

    def __init__(self, embed_dim: int = 64, conflict_threshold: float = 0.6):
        super().__init__()
        self.embedder           = ClaimEmbedder(embed_dim)
        self.conflict_threshold = conflict_threshold

        # Pairwise MLP: concat(emb_i, emb_j) → conflict score in [0, 1]
        self.conflict_scorer = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    # ── Rule-based conflict checks ─────────────────────────────────────

    @staticmethod
    def _object_conflict(c1: StructuredClaim, c2: StructuredClaim) -> bool:
        """Same subject + relation, different objects → contradiction."""
        return (
            c1.subject   == c2.subject
            and c1.relation  == c2.relation
            and c1.object    != c2.object
        )

    @staticmethod
    def _relation_conflict(c1: StructuredClaim, c2: StructuredClaim) -> bool:
        """Same subject + object, mutually exclusive relations."""
        if c1.subject != c2.subject or c1.object != c2.object:
            return False
        pair = frozenset({c1.relation, c2.relation})
        return pair in EXCLUSIVE_RELATION_PAIRS

    @staticmethod
    def _symmetric_conflict(c1: StructuredClaim, c2: StructuredClaim) -> bool:
        """A→B and B→A for an asymmetric relation."""
        return (
            c1.relation in ASYMMETRIC_RELATIONS
            and c1.relation == c2.relation
            and c1.subject  == c2.object
            and c1.object   == c2.subject
        )

    def _rule_score(self, c1: StructuredClaim, c2: StructuredClaim) -> Tuple[float, str]:
        if self._object_conflict(c1, c2):
            return 1.0, "object_conflict"
        if self._relation_conflict(c1, c2):
            return 1.0, "relation_conflict"
        if self._symmetric_conflict(c1, c2):
            return 1.0, "symmetric_conflict"
        return 0.0, "none"

    # ── Main detection logic ───────────────────────────────────────────

    def detect(
        self,
        claims: List[StructuredClaim],
    ) -> Tuple[List[StructuredClaim], List[StructuredClaim], Dict]:
        """
        Scan all claim pairs for conflicts.

        Parameters
        ----------
        claims : all claims generated so far in this forward pass.

        Returns
        -------
        clean_claims   : claims not involved in any conflict.
        flagged_claims : claims that were part of a conflicting pair.
        report         : detailed conflict report dict for logging.
        """
        if len(claims) < 2:
            return claims, [], {"conflicts": [], "suppressed": 0, "clean": len(claims)}

        embeddings     = [self.embedder.embed(c) for c in claims]
        flagged_idx    = set()
        conflict_log   = []

        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                # Rule-based check (fast)
                rule_score, rule_type = self._rule_score(claims[i], claims[j])

                # Learned check (soft conflicts)
                ei, ej = embeddings[i], embeddings[j]   # (1, D) each
                pair_feat = torch.cat([ei, ej], dim=-1)  # (1, 2D)
                with torch.no_grad():
                    learned_score = self.conflict_scorer(pair_feat).item()

                # Take the maximum of both scores
                final_score = max(rule_score, learned_score)
                detected_by = "rule" if rule_score >= 1.0 else (
                    "learned" if learned_score >= self.conflict_threshold else "none"
                )

                if final_score >= self.conflict_threshold:
                    flagged_idx.update([i, j])
                    conflict_log.append({
                        "claim_a"     : claims[i].to_text(),
                        "claim_b"     : claims[j].to_text(),
                        "score"       : round(final_score, 3),
                        "type"        : rule_type if rule_score >= 1.0 else "learned_soft",
                        "detected_by" : detected_by,
                    })

        clean_claims   = [c for k, c in enumerate(claims) if k not in flagged_idx]
        flagged_claims = [c for k, c in enumerate(claims) if k in flagged_idx]

        report = {
            "conflicts"  : conflict_log,
            "suppressed" : len(flagged_claims),
            "clean"      : len(clean_claims),
            "total"      : len(claims),
        }

        return clean_claims, flagged_claims, report
