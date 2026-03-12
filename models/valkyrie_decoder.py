"""
valkyrie_decoder.py
===================
VALKYRIE-Decoder — Complete Model (v2, all novelties integrated)

Full architecture per decoder layer:
┌────────────────────────────────────────────────────────────────┐
│  Input embeddings                                              │
│       ↓                                                        │
│  ┌─────────────────┐        ┌──────────────────┐              │
│  │   Stream A       │        │    Stream B       │              │
│  │  (Knowledge)     │        │  (Generation)     │              │
│  │  TransformerBlock│        │  TransformerBlock │              │
│  └────────┬────────┘        └────────┬─────────┘              │
│           │                          │                          │
│           └──── BidirectionalCSA ────┘   ← NOVELTY #1          │
│                  (A ↔ B mutual attn)                            │
│                          │                                      │
│                  VeracityGate(dynamic)    ← NOVELTY #2          │
│                  (KB verify + dyn thresh)                       │
│                          │                                      │
│                  ConflictDetector         ← NOVELTY #3          │
│                  (pairwise contradiction                        │
│                   suppression)                                  │
│                          │                                      │
│                    next layer...                                │
└────────────────────────────────────────────────────────────────┘
                          │
                   Output projection
                          │
                     Vocabulary logits
"""

from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn

from models.knowledge_base import KnowledgeBase
from models.structures import StructuredClaim
from models.transformer_blocks import PositionalEncoding, TransformerBlock
from models.bidirectional_stream import BidirectionalCrossStreamAttention
from models.veracity_gate import VeracityGate
from models.conflict_detector import ConflictDetector


class ValkyrieDecoder(nn.Module):
    """
    Full VALKYRIE-Decoder with all novelty enhancements.

    Parameters
    ----------
    vocab_size : size of the token vocabulary.
    d_model    : hidden dimension (both streams).
    n_heads    : number of attention heads.
    n_layers   : number of decoder layers per stream.
    d_ff       : feed-forward inner dimension.
    max_len    : maximum sequence length.
    dropout    : dropout rate throughout the model.
    """

    def __init__(
        self,
        vocab_size : int,
        d_model    : int   = 256,
        n_heads    : int   = 8,
        n_layers   : int   = 4,
        d_ff       : int   = 512,
        max_len    : int   = 512,
        dropout    : float = 0.1,
    ):
        super().__init__()

        self.d_model    = d_model
        self.n_heads    = n_heads
        self.n_layers   = n_layers
        self.vocab_size = vocab_size

        # Shared knowledge base
        self.knowledge_base = KnowledgeBase()

        # ── Embeddings ─────────────────────────────────────────────────
        self.token_embedding    = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.positional_encoding = PositionalEncoding(d_model, max_len, dropout)

        # ── Stream A: Knowledge/Context Stream ─────────────────────────
        self.stream_a_layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        # ── Stream B: Generation/Language Stream ───────────────────────
        self.stream_b_layers = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        # ── NOVELTY #1: Bidirectional Cross-Stream Attention ───────────
        self.bidir_cross_attn = nn.ModuleList([
            BidirectionalCrossStreamAttention(d_model, n_heads, dropout)
            for _ in range(n_layers)
        ])

        # ── NOVELTY #2: Veracity Gates with Dynamic Threshold ──────────
        self.veracity_gates = nn.ModuleList([
            VeracityGate(d_model, self.knowledge_base, n_layers, i)
            for i in range(n_layers)
        ])

        # ── NOVELTY #3: Claim Conflict Detector ────────────────────────
        self.conflict_detector = ConflictDetector(embed_dim=64, conflict_threshold=0.6)

        # ── Output projection ──────────────────────────────────────────
        self.output_norm  = nn.LayerNorm(d_model)
        self.output_layer = nn.Linear(d_model, vocab_size)

        # ── Minimal internal vocabulary ────────────────────────────────
        self.vocabulary: Dict = {
            "word_to_idx": {"<PAD>": 0, "<SOS>": 1, "<EOS>": 2},
            "idx_to_word": {0: "<PAD>", 1: "<SOS>", 2: "<EOS>"},
        }

        # Initialise weights
        self._init_weights()

    def _init_weights(self) -> None:
        """Xavier uniform initialisation for linear layers."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0, std=0.02)

    # ── Forward pass ──────────────────────────────────────────────────

    def forward(
        self,
        input_ids      : torch.Tensor,
        generate_claims: bool = True,
        mask           : Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """
        Full dual-stream forward pass with all novelty components.

        Parameters
        ----------
        input_ids       : (B, T) long tensor of token indices.
        generate_claims : run veracity gating and collect claims.
        mask            : optional attention mask (B, T).

        Returns
        -------
        dict with keys:
            logits           – (B, T, vocab_size) output logits.
            claims           – verified, conflict-free claims.
            flagged_claims   – claims suppressed by conflict detection.
            gate_states      – per-layer gate diagnostic info.
            conflict_reports – per-layer conflict report.
            stream_a         – final Stream A hidden states.
            stream_b         – final Stream B hidden states.
        """
        # ── Embed input ────────────────────────────────────────────────
        x = self.token_embedding(input_ids)     # (B, T, d_model)
        x = self.positional_encoding(x)

        stream_a = x.clone()
        stream_b = x.clone()

        # Accumulators
        all_claims      : List[StructuredClaim] = []
        all_flagged     : List[StructuredClaim] = []
        gate_states     : List[Dict]            = []
        conflict_reports: List[Dict]            = []

        # ── Layer-by-layer processing ──────────────────────────────────
        for i, (layer_a, layer_b, bidir, gate) in enumerate(
            zip(
                self.stream_a_layers,
                self.stream_b_layers,
                self.bidir_cross_attn,
                self.veracity_gates,
            )
        ):
            # Independent stream processing
            stream_a = layer_a(stream_a, mask)
            stream_b = layer_b(stream_b, mask)

            # NOVELTY #1: Bidirectional mutual attention
            stream_a, stream_b = bidir(stream_a, stream_b)

            if generate_claims:
                # NOVELTY #2: Veracity gate with dynamic threshold
                gated_b, confidence, gate_open, meta = gate.verify_and_gate(
                    stream_a, stream_b, self.vocabulary
                )

                # Collect claim
                claim = gate.extract_claim(stream_b, self.vocabulary, i)
                if claim is not None:
                    claim.verified   = gate_open
                    claim.confidence = confidence
                    claim.layer      = i
                    all_claims.append(claim)

                # NOVELTY #3: Conflict detection across all claims so far
                if len(all_claims) >= 2:
                    clean, flagged, report = self.conflict_detector.detect(all_claims)
                    all_claims  = clean
                    all_flagged.extend(flagged)
                    conflict_reports.append({**report, "layer": i})

                # Record gate state for logging
                gate_states.append({
                    "layer"             : i,
                    "gate_open"         : gate_open,
                    "confidence"        : round(confidence, 4),
                    "dynamic_threshold" : meta.get("dynamic_threshold", 0.0),
                    "query_type"        : meta.get("query_type", "Unknown"),
                    "gate_value"        : meta.get("gate_value", 0.0),
                    "reason"            : meta.get("reason", ""),
                })

                stream_b = gated_b

        # ── Output ────────────────────────────────────────────────────
        out     = self.output_norm(stream_b)
        logits  = self.output_layer(out)     # (B, T, vocab_size)

        return {
            "logits"          : logits,
            "claims"          : all_claims,
            "flagged_claims"  : all_flagged,
            "gate_states"     : gate_states,
            "conflict_reports": conflict_reports,
            "stream_a"        : stream_a,
            "stream_b"        : stream_b,
        }

    # ── Text generation ───────────────────────────────────────────────

    def generate(
        self,
        prompt     : str,
        max_length : int = 20,
    ) -> Tuple[str, List[StructuredClaim], List[Dict]]:
        """
        Greedy decoding with full veracity-gated pipeline.

        Returns
        -------
        (generated_text, verified_claims, gate_states)
        """
        self.eval()
        # Simplified tokenisation: each word → random token index
        input_tensor = torch.randint(
            3, self.vocab_size, (1, max(1, len(prompt.split())))
        )

        generated  : List[int]            = []
        all_claims : List[StructuredClaim] = []
        all_gates  : List[Dict]           = []

        with torch.no_grad():
            for step in range(max_length):
                outputs    = self.forward(input_tensor, generate_claims=True)
                next_token = torch.argmax(outputs["logits"][0, -1, :]).item()

                generated.append(next_token)
                all_claims.extend(outputs["claims"])
                all_gates.extend(outputs["gate_states"])

                input_tensor = torch.cat(
                    [input_tensor, torch.tensor([[next_token]])], dim=1
                )

                if next_token == 2:   # <EOS>
                    break

        text = " ".join(f"token_{t}" for t in generated)
        return text, all_claims, all_gates

    def parameter_count(self) -> Dict[str, int]:
        """Return parameter counts broken down by component."""
        def count(module):
            return sum(p.numel() for p in module.parameters())

        return {
            "embeddings"       : count(self.token_embedding) + count(self.positional_encoding),
            "stream_a"         : count(self.stream_a_layers),
            "stream_b"         : count(self.stream_b_layers),
            "bidir_cross_attn" : count(self.bidir_cross_attn),
            "veracity_gates"   : count(self.veracity_gates),
            "conflict_detector": count(self.conflict_detector),
            "output_layer"     : count(self.output_layer),
            "total"            : count(self),
        }


# ── Extended: ValkyrieWithMemory ──────────────────────────────────────────────

class ValkyrieWithMemory(ValkyrieDecoder):
    """
    VALKYRIE-Decoder with a persistent in-process fact memory.
    Verified claims are cached for fast recall in subsequent steps.
    """

    def __init__(self, *args, memory_size: int = 200, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_size = memory_size
        self.fact_memory : Dict[Tuple[str, str], StructuredClaim] = {}

    def remember_fact(self, claim: StructuredClaim) -> None:
        if claim.verified and len(self.fact_memory) < self.memory_size:
            self.fact_memory[(claim.subject, claim.relation)] = claim

    def recall_fact(self, subject: str, relation: str) -> Optional[StructuredClaim]:
        return self.fact_memory.get((subject, relation))

    def memory_summary(self) -> str:
        if not self.fact_memory:
            return "Memory is empty."
        lines = [
            f"  • {c.to_text()}  (conf={c.confidence:.2f}, layer={c.layer})"
            for c in self.fact_memory.values()
        ]
        return f"Memory ({len(self.fact_memory)} facts):\n" + "\n".join(lines)
