"""
bidirectional_stream.py
=======================
NOVELTY #1 — Bidirectional Cross-Stream Attention

Standard dual-stream models only allow one-way information flow:
    Stream B (generation) attends to Stream A (knowledge)

VALKYRIE v2 makes this BIDIRECTIONAL:
    Stream A  ←──────────────────  Stream B
    (knowledge absorbs             (generation intent
     generation intent)             absorbed into knowledge)

    Stream B  ←──────────────────  Stream A
    (generation absorbs            (factual grounding
     factual grounding)             absorbed into generation)

Why this matters
----------------
In one-way attention, the knowledge stream never updates based on
what the generation stream is doing. This means the knowledge context
becomes stale — it doesn't "know" what direction the language is going.

With bidirectional attention:
- Stream A learns to focus on the facts most relevant to what Stream B
  is currently writing.
- Stream B learns to adjust its word choices based on what Stream A
  knows is true.

This creates a tight feedback loop that forces both streams to stay
semantically aligned throughout the entire decoding process.

Architecture
------------
    Input:   stream_a (B, T, d_model),  stream_b (B, T, d_model)

    Step 1:  b_update = CrossAttn(query=B, key=A, value=A)
             new_b    = LayerNorm(B + gate_b * b_update)

    Step 2:  a_update = CrossAttn(query=A, key=B, value=B)
             new_a    = LayerNorm(A + gate_a * a_update)

    Output:  new_stream_a,  new_stream_b

    gate_a, gate_b are LEARNED scalars — initialised small (0.1)
    so training starts stable and gradually increases cross-influence.
"""

import torch
import torch.nn as nn

from models.transformer_blocks import MultiHeadAttention


class BidirectionalCrossStreamAttention(nn.Module):
    """
    Mutual cross-attention between knowledge stream (A) and generation
    stream (B), with learned gate scalars controlling influence strength.

    Parameters
    ----------
    d_model : int   – hidden dimension (must match both streams).
    n_heads : int   – number of attention heads.
    dropout : float – dropout applied to residual updates.
    """

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()

        # Direction 1: Generation stream (B) attends to Knowledge stream (A)
        # "What does the knowledge stream know that I should write about?"
        self.b_attends_a = MultiHeadAttention(d_model, n_heads, dropout)

        # Direction 2: Knowledge stream (A) attends to Generation stream (B)
        # "What is the generation stream talking about so I can focus on it?"
        self.a_attends_b = MultiHeadAttention(d_model, n_heads, dropout)

        # Layer normalisations for both directions
        self.norm_a = nn.LayerNorm(d_model)
        self.norm_b = nn.LayerNorm(d_model)

        # Learnable gate scalars
        # Initialised at 0.1 — small, so early training is numerically stable
        # The model gradually learns the right influence strength
        self.gate_b = nn.Parameter(torch.tensor(0.1))  # how much B absorbs from A
        self.gate_a = nn.Parameter(torch.tensor(0.1))  # how much A absorbs from B

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        stream_a: torch.Tensor,   # (B, T, d_model)  knowledge stream
        stream_b: torch.Tensor,   # (B, T, d_model)  generation stream
    ):
        """
        Apply bidirectional cross-stream attention.

        Returns
        -------
        (updated_stream_a, updated_stream_b)
        Both tensors have the same shape as the inputs.
        """

        # ── Direction 1: B absorbs from A ─────────────────────────────
        # Generation stream queries the knowledge stream
        b_update  = self.b_attends_a(stream_b, stream_a, stream_a)
        new_b     = self.norm_b(
            stream_b + self.dropout(self.gate_b * b_update)
        )

        # ── Direction 2: A absorbs from B ─────────────────────────────
        # Knowledge stream queries the generation stream
        a_update  = self.a_attends_b(stream_a, stream_b, stream_b)
        new_a     = self.norm_a(
            stream_a + self.dropout(self.gate_a * a_update)
        )

        return new_a, new_b

    def gate_values(self) -> dict:
        """Return current learned gate values for monitoring."""
        return {
            "gate_a (knowledge absorbs generation)": round(self.gate_a.item(), 4),
            "gate_b (generation absorbs knowledge)": round(self.gate_b.item(), 4),
        }
