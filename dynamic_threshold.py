"""
dynamic_threshold.py
====================
NOVELTY #2 — Dynamic Veracity Threshold

Problem with fixed thresholds
------------------------------
In VALKYRIE v1, the gate used a hardcoded threshold of 0.7.
This means every question — factual, opinion, temporal — was
evaluated with the same strictness. This is wrong because:

  "Who founded Apple?"        → stable fact → 0.75 strictness is right
  "What's the best phone?"    → opinion     → 0.40 is more appropriate
  "What is France's GDP now?" → changes     → 0.85 needed (careful!)

Solution
--------
DynamicVeracityThreshold computes a PER-SAMPLE, PER-LAYER threshold
as a learned function of three signals:

  1. Query Type     – what kind of question is being asked?
  2. Stream Confidence – how strongly is the knowledge stream activating?
  3. Layer Depth    – how deep in the network are we?

Query Type Taxonomy
-------------------
  Type 0 – FACTUAL    (who, what, where, when)  → threshold bias 0.75
  Type 1 – RELATIONAL (how does X relate to Y)  → threshold bias 0.60
  Type 2 – OPINION    (best, should, could)      → threshold bias 0.40
  Type 3 – TEMPORAL   (current, now, latest)     → threshold bias 0.85
                                                    (strictest: facts change)

Architecture
------------
  stream_a → QueryTypeClassifier → query_probs (4,)
  stream_a → mean pooling → norm → sigmoid → stream_conf (1,)
  layer_idx / n_layers → depth (1,)

  features = concat(query_probs, stream_conf, depth)  # 6-dim
  threshold = MLP(features)                           # scalar in [0,1]
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


# ── Query type labels for logging ─────────────────────────────────────────────
QUERY_TYPE_NAMES = ["Factual", "Relational", "Opinion", "Temporal"]

# Interpretable starting biases per query type (used to initialise the MLP)
# Higher = stricter gate = harder for claims to pass through
QUERY_TYPE_BIASES = {
    "Factual"   : 0.75,
    "Relational": 0.60,
    "Opinion"   : 0.40,
    "Temporal"  : 0.85,
}


class QueryTypeClassifier(nn.Module):
    """
    Classifies the query into one of 4 types based on Stream A's hidden states.

    Input  : stream_a (B, T, d_model)
    Output : query_type_probs (B, 4)  — soft probabilities over 4 types
    """

    NUM_TYPES = 4

    def __init__(self, d_model: int):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, self.NUM_TYPES),
        )

    def forward(self, stream_a: torch.Tensor) -> torch.Tensor:
        """
        Mean-pool Stream A across the sequence dimension,
        then classify into query types.

        Returns soft probability distribution over 4 types.
        """
        pooled = stream_a.mean(dim=1)                      # (B, d_model)
        logits = self.classifier(pooled)                   # (B, 4)
        return F.softmax(logits, dim=-1)                   # (B, 4)


class DynamicVeracityThreshold(nn.Module):
    """
    Produces a context-sensitive gate threshold for each sample and layer.

    The output threshold is a scalar in [0, 1] representing
    "how confident does a claim need to be to pass the gate?"

    Higher threshold = stricter = fewer claims pass.
    Lower  threshold = lenient  = more claims pass.

    Parameters
    ----------
    d_model     : hidden dimension of transformer streams.
    n_layers    : total number of decoder layers (for depth normalisation).
    base_thresh : default threshold before context adjustment.
    """

    # Per-type base threshold biases
    TYPE_BIAS_TENSOR = torch.tensor(
        [0.75, 0.60, 0.40, 0.85],   # Factual, Relational, Opinion, Temporal
        dtype=torch.float32,
    )

    def __init__(
        self,
        d_model     : int,
        n_layers    : int,
        base_thresh : float = 0.65,
    ):
        super().__init__()
        self.n_layers    = max(n_layers, 1)
        self.base_thresh = base_thresh

        # Query type classifier
        self.query_classifier = QueryTypeClassifier(d_model)

        # Threshold MLP
        # Input:  [query_type_probs(4) | stream_conf(1) | layer_depth(1)] = 6 dims
        # Output: threshold scalar in [0, 1]
        self.threshold_mlp = nn.Sequential(
            nn.Linear(6, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),     # ensures output is always in [0, 1]
        )

        # Register bias tensor as buffer (auto-moved to correct device)
        self.register_buffer("type_biases", self.TYPE_BIAS_TENSOR)

    def forward(
        self,
        stream_a       : torch.Tensor,
        layer_idx      : int,
        base_confidence: float = 0.5,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute the dynamic threshold.

        Parameters
        ----------
        stream_a        : (B, T, d_model) knowledge stream hidden states.
        layer_idx       : current layer index (0-based).
        base_confidence : confidence from KB lookup (used as hint).

        Returns
        -------
        threshold  : (B, 1) per-sample gate threshold.
        query_type : (B, 4) soft query-type distribution for logging.
        """
        B      = stream_a.size(0)
        device = stream_a.device

        # Signal 1: Query type probabilities
        query_type = self.query_classifier(stream_a)          # (B, 4)

        # Signal 2: Stream A activation magnitude → proxy for model confidence
        stream_conf = stream_a.mean(dim=1).norm(dim=-1, keepdim=True)  # (B, 1)
        stream_conf = torch.sigmoid(stream_conf)               # normalise to (0,1)

        # Signal 3: Normalised layer depth (0 = first layer, 1 = last layer)
        depth = torch.full(
            (B, 1), layer_idx / self.n_layers,
            dtype=torch.float32, device=device
        )

        # Combine all signals
        features  = torch.cat([query_type, stream_conf, depth], dim=-1)  # (B, 6)
        threshold = self.threshold_mlp(features)                          # (B, 1)

        return threshold, query_type

    def query_type_name(self, query_type_probs: torch.Tensor) -> str:
        """Return the dominant query type label for the first batch sample."""
        idx = query_type_probs[0].argmax().item()
        return QUERY_TYPE_NAMES[int(idx)]

    def threshold_explanation(
        self,
        query_type_probs : torch.Tensor,
        threshold        : torch.Tensor,
        layer_idx        : int,
    ) -> str:
        """Human-readable explanation of why this threshold was chosen."""
        qt   = self.query_type_name(query_type_probs)
        bias = QUERY_TYPE_BIASES[qt]
        t    = threshold.mean().item()
        return (
            f"Query type: {qt} (bias={bias}) | "
            f"Layer: {layer_idx}/{self.n_layers} | "
            f"Final threshold: {t:.3f}"
        )
