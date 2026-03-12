"""
transformer_blocks.py
=====================
Reusable transformer building blocks used by both streams
of the VALKYRIE-Decoder.

Classes
-------
PositionalEncoding  – sinusoidal positional encoding
MultiHeadAttention  – scaled dot-product multi-head attention
FeedForward         – position-wise feed-forward network
TransformerBlock    – full pre-norm transformer layer
"""

import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionalEncoding(nn.Module):
    """
    Sinusoidal positional encoding (Vaswani et al., 2017).
    Adds position information to token embeddings.
    """

    def __init__(self, d_model: int, max_len: int = 512, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        pe       = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10_000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))   # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to *x* of shape (B, T, d_model)."""
        return self.dropout(x + self.pe[:, : x.size(1)])


class MultiHeadAttention(nn.Module):
    """
    Scaled dot-product multi-head attention.

    Supports self-attention and cross-attention (query != key/value).
    """

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k     = d_model // n_heads

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query : torch.Tensor,
        key   : torch.Tensor,
        value : torch.Tensor,
        mask  : Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        B = query.size(0)

        # Project and split into heads
        Q = self.W_q(query).view(B, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key  ).view(B, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(B, -1, self.n_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attn = self.dropout(F.softmax(scores, dim=-1))

        # Weighted sum + reshape
        context = torch.matmul(attn, V)
        context = context.transpose(1, 2).contiguous().view(B, -1, self.d_model)
        return self.W_o(context)


class FeedForward(nn.Module):
    """
    Position-wise feed-forward network with GELU activation.
    Applied independently to each position.
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TransformerBlock(nn.Module):
    """
    Standard transformer encoder/decoder block.

    Structure (post-norm):
        x → Self-Attention → Add & Norm → Feed-Forward → Add & Norm
    """

    def __init__(
        self,
        d_model  : int,
        n_heads  : int,
        d_ff     : int,
        dropout  : float = 0.1,
    ):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.ff        = FeedForward(d_model, d_ff, dropout)
        self.norm1     = nn.LayerNorm(d_model)
        self.norm2     = nn.LayerNorm(d_model)
        self.dropout   = nn.Dropout(dropout)

    def forward(
        self,
        x    : torch.Tensor,
        mask : Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # Self-attention sub-layer
        attn_out = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))

        # Feed-forward sub-layer
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout(ff_out))
        return x
