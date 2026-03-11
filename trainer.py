"""
trainer.py
==========
Training and evaluation loop for VALKYRIE-Decoder.

Losses
------
1. Language Model Loss  – standard cross-entropy on token prediction.
2. Truth Penalty        – penalises low-confidence claims (encourages
                          the model to make verifiable assertions).
3. Conflict Penalty     – penalises batches where conflicts are detected
                          (encourages the model to be self-consistent).

The combined loss:
    total = lm_loss
          + α * truth_penalty
          + β * conflict_penalty
"""

from typing import Dict, List, Optional
import torch
import torch.nn as nn

from models.valkyrie_decoder import ValkyrieDecoder
from models.structures import StructuredClaim


class ValkyrieTrainer:
    """
    Training wrapper for ValkyrieDecoder.

    Parameters
    ----------
    model                  : ValkyrieDecoder instance.
    lr                     : learning rate for Adam optimiser.
    truth_penalty_weight   : α — weight for truth regularisation term.
    conflict_penalty_weight: β — weight for conflict regularisation term.
    grad_clip              : max gradient norm for clipping.
    """

    def __init__(
        self,
        model                   : ValkyrieDecoder,
        lr                      : float = 1e-3,
        truth_penalty_weight    : float = 0.1,
        conflict_penalty_weight : float = 0.05,
        grad_clip               : float = 1.0,
    ):
        self.model                   = model
        self.grad_clip               = grad_clip
        self.truth_penalty_weight    = truth_penalty_weight
        self.conflict_penalty_weight = conflict_penalty_weight

        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=lr, betas=(0.9, 0.98), eps=1e-9
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", patience=3, factor=0.5
        )
        # Ignore padding index 0
        self.criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=0.1)

    # ── Training step ─────────────────────────────────────────────────

    def train_step(
        self,
        input_ids  : torch.Tensor,
        target_ids : torch.Tensor,
    ) -> Dict[str, float]:
        """
        One forward + backward + optimiser step.

        Parameters
        ----------
        input_ids  : (B, T) — token indices fed to the model.
        target_ids : (B, T) — ground-truth token indices.

        Returns
        -------
        dict with: loss, lm_loss, truth_penalty, conflict_penalty,
                   claims_generated, conflicts_detected.
        """
        self.model.train()
        self.optimizer.zero_grad()

        # Forward pass (skip claim generation for speed during training)
        outputs = self.model(input_ids, generate_claims=True)
        logits  = outputs["logits"]   # (B, T, V)

        # ── Loss 1: Language model cross-entropy ──────────────────────
        lm_loss = self.criterion(
            logits.view(-1, logits.size(-1)),
            target_ids.view(-1),
        )

        # ── Loss 2: Truth penalty ─────────────────────────────────────
        # Penalise low-confidence claims to encourage factual assertions
        claims        = outputs.get("claims", [])
        truth_penalty = torch.tensor(0.0)
        if claims:
            avg_conf      = sum(c.confidence for c in claims) / len(claims)
            truth_penalty = torch.tensor(
                max(0.0, 1.0 - avg_conf), dtype=torch.float32
            )

        # ── Loss 3: Conflict penalty ──────────────────────────────────
        # Penalise batches with detected conflicts
        flagged          = outputs.get("flagged_claims", [])
        conflict_penalty = torch.tensor(0.0)
        if flagged:
            conflict_penalty = torch.tensor(
                len(flagged) / max(len(claims) + len(flagged), 1),
                dtype=torch.float32,
            )

        # ── Combined loss ─────────────────────────────────────────────
        total_loss = (
            lm_loss
            + self.truth_penalty_weight    * truth_penalty
            + self.conflict_penalty_weight * conflict_penalty
        )

        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
        self.optimizer.step()

        return {
            "loss"               : round(total_loss.item(), 6),
            "lm_loss"            : round(lm_loss.item(), 6),
            "truth_penalty"      : round(truth_penalty.item(), 6),
            "conflict_penalty"   : round(conflict_penalty.item(), 6),
            "claims_generated"   : len(claims),
            "conflicts_detected" : len(flagged),
        }

    # ── Evaluation step ───────────────────────────────────────────────

    @torch.no_grad()
    def evaluate_step(
        self,
        input_ids  : torch.Tensor,
        target_ids : torch.Tensor,
    ) -> Dict[str, float]:
        """Same as train_step but without gradient updates."""
        self.model.eval()
        outputs = self.model(input_ids, generate_claims=True)
        logits  = outputs["logits"]

        lm_loss = self.criterion(
            logits.view(-1, logits.size(-1)),
            target_ids.view(-1),
        )

        claims   = outputs.get("claims", [])
        verified = sum(1 for c in claims if c.verified)

        return {
            "eval_loss"      : round(lm_loss.item(), 6),
            "claims"         : len(claims),
            "verified"       : verified,
            "verification_%" : round(verified / max(len(claims), 1) * 100, 1),
        }

    def update_scheduler(self, val_loss: float) -> None:
        """Step the LR scheduler based on validation loss."""
        self.scheduler.step(val_loss)

    def current_lr(self) -> float:
        return self.optimizer.param_groups[0]["lr"]
