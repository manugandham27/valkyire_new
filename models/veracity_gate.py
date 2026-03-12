"""
veracity_gate.py
================
Veracity-Gated Fusion Layer

Controls information flow from the generation stream (Stream B) into
the final output based on two criteria:
  1. The claim encoded in Stream B is verifiable in the Knowledge Base.
  2. The claim's confidence exceeds the DYNAMIC threshold (Novelty #2).

Gate Logic
----------
  For each claim:
    - Look it up in the Knowledge Base → (is_true, confidence)
    - Compute dynamic threshold from stream context
    - If confidence >= threshold AND is_true:
          gate OPENS  → stream B multiplied by gate_value (amplified)
    - Else:
          gate CLOSES → stream B multiplied by (1 - gate_value) (suppressed)

  gate_value itself is learned by a small MLP operating on the
  concatenation of mean-pooled Stream A and Stream B.
"""

import torch
import torch.nn as nn
from typing import Dict, Optional, Tuple

from models.structures import StructuredClaim
from models.knowledge_base import KnowledgeBase
from models.transformer_blocks import MultiHeadAttention
from models.dynamic_threshold import DynamicVeracityThreshold


class VeracityGate(nn.Module):
    """
    Veracity-Gated Fusion Layer with dynamic threshold support.

    Parameters
    ----------
    d_model    : hidden dimension.
    knowledge_base : KnowledgeBase instance for fact verification.
    n_layers   : total decoder layers (for depth-aware threshold).
    layer_idx  : index of the current layer (0-based).
    """

    # Simplified vocabulary for claim extraction
    SUBJECTS  = [
        "Eiffel Tower", "Paris", "Apple", "Tokyo", "Mars",
        "Microsoft", "London", "Einstein", "Amazon", "Tesla",
    ]
    RELATIONS = [
        "located_in", "capital_of", "founded_by",
        "population_of", "discovered", "color",
    ]
    OBJECTS   = [
        "Paris", "France", "Steve Jobs", "37 million", "Red",
        "Bill Gates", "9 million", "Relativity", "Jeff Bezos", "Elon Musk",
    ]

    def __init__(
        self,
        d_model        : int,
        knowledge_base : KnowledgeBase,
        n_layers       : int = 4,
        layer_idx      : int = 0,
    ):
        super().__init__()
        self.knowledge_base = knowledge_base
        self.layer_idx      = layer_idx

        # Dynamic threshold (replaces fixed 0.7 from v1)
        self.dynamic_threshold = DynamicVeracityThreshold(d_model, n_layers)

        # Gate MLP: concat(mean_A, mean_B) → scalar gate in [0, 1]
        self.gate_network = nn.Sequential(
            nn.Linear(d_model * 2, d_model),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid(),
        )

        # Simplified claim extractor: hidden state → 3 logits
        self.claim_extractor = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, 3),
        )

    # ── Claim extraction ───────────────────────────────────────────────

    def extract_claim(
        self,
        hidden_state : torch.Tensor,
        vocabulary   : Dict,
        layer_idx    : int = -1,
    ) -> Optional[StructuredClaim]:
        """
        Extract a StructuredClaim from hidden states via learned projection.
        """
        logits = self.claim_extractor(hidden_state.mean(dim=1))  # (B, 3)
        try:
            s = int(torch.argmax(logits[0, 0]).item()) % len(self.SUBJECTS)
            r = int(torch.argmax(logits[0, 1]).item()) % len(self.RELATIONS)
            o = int(torch.argmax(logits[0, 2]).item()) % len(self.OBJECTS)
            return StructuredClaim(
                subject    = self.SUBJECTS[s],
                relation   = self.RELATIONS[r],
                object     = self.OBJECTS[o],
                confidence = 0.8,
                layer      = layer_idx,
            )
        except Exception:
            return None

    # ── Gate logic ────────────────────────────────────────────────────

    def verify_and_gate(
        self,
        stream_a   : torch.Tensor,
        stream_b   : torch.Tensor,
        vocabulary : Dict,
    ) -> Tuple[torch.Tensor, float, bool, Dict]:
        """
        Full gate pipeline:
          extract claim → verify → compute dynamic threshold → gate.

        Returns
        -------
        gated_stream_b : modified stream B tensor.
        confidence     : KB confidence (0.0 if not found).
        gate_open      : whether the gate opened.
        meta           : logging dict (threshold, query_type, etc.).
        """
        claim = self.extract_claim(stream_b, vocabulary, self.layer_idx)
        if claim is None:
            return stream_b, 0.0, False, {"reason": "no_claim_extracted"}

        # Knowledge base verification
        is_true, confidence = self.knowledge_base.verify_claim(claim)

        # Dynamic threshold (Novelty #2)
        threshold, query_type = self.dynamic_threshold(
            stream_a, self.layer_idx, confidence
        )

        # Gate scalar
        gate_input = torch.cat(
            [stream_a.mean(dim=1), stream_b.mean(dim=1)], dim=-1
        )
        gate_value = self.gate_network(gate_input)   # (B, 1)

        # Gate decision: compare per-sample confidence vs dynamic threshold
        conf_tensor = torch.full_like(threshold, confidence)
        gate_open   = bool(is_true and (conf_tensor >= threshold).all().item())

        # Apply gate
        if gate_open:
            gated_stream = stream_b * gate_value.unsqueeze(-1)
        else:
            gated_stream = stream_b * (1.0 - gate_value.unsqueeze(-1))

        # Build metadata for logging
        threshold_val = threshold.mean().item()
        qt_name       = self.dynamic_threshold.query_type_name(query_type)
        meta = {
            "claim"             : claim.to_dict(),
            "is_true"           : is_true,
            "confidence"        : round(confidence, 4),
            "dynamic_threshold" : round(threshold_val, 4),
            "query_type"        : qt_name,
            "gate_open"         : gate_open,
            "gate_value"        : round(gate_value.mean().item(), 4),
            "layer_idx"         : self.layer_idx,
            "reason"            : (
                "verified_above_threshold" if gate_open
                else ("false_claim" if not is_true else "below_threshold")
            ),
        }

        return gated_stream, confidence, gate_open, meta


class AdvancedVeracityGate(VeracityGate):
    """
    Enhanced gate using multi-head attention for claim extraction.
    Suitable for deeper models where positional context matters.
    """

    def __init__(
        self,
        d_model        : int,
        knowledge_base : KnowledgeBase,
        n_layers       : int = 4,
        layer_idx      : int = 0,
        n_heads        : int = 4,
    ):
        super().__init__(d_model, knowledge_base, n_layers, layer_idx)
        self.claim_attention  = MultiHeadAttention(d_model, n_heads)
        self.claim_projection = nn.Linear(d_model, 128)

    def extract_claim_with_attention(
        self, hidden_state: torch.Tensor
    ) -> torch.Tensor:
        """Use self-attention to focus on claim-relevant tokens."""
        attended  = self.claim_attention(hidden_state, hidden_state, hidden_state)
        projected = self.claim_projection(attended.mean(dim=1))
        return projected   # (B, 128) claim embedding
