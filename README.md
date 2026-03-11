# VALKYRIE-Decoder  v2

**Dual-Stream Structured Claim Co-Generation with Veracity-Gated Transformer Decoding**

---

## Architecture Flow

```
Input Query / Prompt
        │
        ▼
 Context Encoder
 (token embedding + positional encoding)
        │
        ▼
 Shared Latent Knowledge Representation
        │
        ▼
┌───────────────────────────────────────────────────────┐
│              DUAL-STREAM TRANSFORMER DECODER           │
│                                                       │
│   ┌─────────────────┐       ┌──────────────────┐      │
│   │   STREAM A       │       │    STREAM B       │      │
│   │  Knowledge /     │       │  Generation /     │      │
│   │  Context stream  │       │  Language stream  │      │
│   │  TransformerBlock│       │  TransformerBlock │      │
│   └────────┬────────┘       └────────┬──────────┘      │
│            │                         │                  │
│            └──── ★ NOVELTY #1 ───────┘                  │
│              BidirectionalCrossStreamAttention          │
│                   A ←──────────────→ B                  │
│              (mutual influence, learned gates)          │
│                         │                               │
│                         ▼                               │
│               Claim Graph Constructor                   │
│               Token Sequence Builder                    │
│                         │                               │
│                         ▼                               │
│            ★ NOVELTY #3 — Conflict Detector            │
│             Pairwise claim contradiction check          │
│             Both claims suppressed if conflict          │
│              • Object conflict                          │
│              • Relation conflict                        │
│              • Symmetric conflict                       │
│                         │                               │
│                         ▼                               │
│         ★ NOVELTY #2 — Epistemic Fusion Layer          │
│           Veracity Gate + Dynamic Threshold             │
│           Knowledge Base verification                   │
│           Query-type aware threshold:                   │
│             Factual   → 0.75                            │
│             Relational→ 0.60                            │
│             Opinion   → 0.40                            │
│             Temporal  → 0.85  (strictest)               │
│           Layer-depth scaling                           │
│                         │                               │
│                  (repeat N layers)                      │
└─────────────────────────┼─────────────────────────────┘
                          │
                          ▼
                   Output Generator
                   (Layer Norm → Linear → logits)
                          │
                          ▼
              Final verified text output
```

---

## Project Structure

```
valkyrie_final/
├── main.py                       ← Entry point
├── requirements.txt
├── .vscode/
│   ├── launch.json               ← 5 pre-built run configs
│   └── settings.json
│
├── models/
│   ├── __init__.py
│   ├── structures.py             ← StructuredClaim dataclass
│   ├── knowledge_base.py         ← KnowledgeBase (facts + verification)
│   ├── transformer_blocks.py     ← MHA, FeedForward, TransformerBlock
│   ├── bidirectional_stream.py   ★ BidirectionalCrossStreamAttention
│   ├── dynamic_threshold.py      ★ DynamicVeracityThreshold
│   ├── conflict_detector.py      ★ ConflictDetector
│   ├── veracity_gate.py          ← VeracityGate (uses dynamic threshold)
│   └── valkyrie_decoder.py       ← ValkyrieDecoder, ValkyrieWithMemory
│
├── training/
│   ├── __init__.py
│   └── trainer.py                ← ValkyrieTrainer (3-term loss)
│
├── utils/
│   ├── __init__.py
│   └── vocab.py                  ← Vocabulary helpers
│
└── demo/
    ├── __init__.py
    └── demo.py                   ← Full 10-section demonstration
```

---

## Setup & Run

```bash
# Step 1 — Create virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Step 2 — Install dependencies
pip install -r requirements.txt

# Step 3 — Run
python main.py                   # full automated demo
python main.py --interactive     # demo + interactive prompts
python main.py --interactive --no-demo   # interactive only
python main.py --test            # quick sanity check
```

---

## VS Code — Run Configs (F5)

| Profile | Description |
|---|---|
| ▶ Run Full Demo | Complete 10-section automated demo |
| ▶ Interactive Mode (with demo) | Demo first, then type your own prompts |
| ▶ Interactive Mode only | Skip demo, go straight to prompts |
| ▶ Quick Sanity Test | Fast shape/output check |
| ▶ Demo script directly | Run demo/demo.py standalone |

---

## The 3 Novelty Additions

### ★ #1 — Bidirectional Cross-Stream Attention
**File:** `models/bidirectional_stream.py`

Makes Stream A (knowledge) and Stream B (generation) mutually attend to each other at every layer. Previously, only B → A was possible. Now A ↔ B with learned gate scalars.

### ★ #2 — Dynamic Veracity Threshold
**File:** `models/dynamic_threshold.py`

Replaces fixed threshold (0.7) with a learned, context-sensitive value that adapts based on: query type (Factual/Relational/Opinion/Temporal), stream A activation confidence, and layer depth.

### ★ #3 — Claim Conflict Detection
**File:** `models/conflict_detector.py`

Scans all generated claims pairwise for contradictions before they reach the output. Three conflict types: object conflict, relation conflict, symmetric conflict. Both claims in a conflicting pair are suppressed.

---

## Training Loss

```
total_loss = lm_loss
           + 0.10 × truth_penalty    (penalises low-confidence claims)
           + 0.05 × conflict_penalty (penalises batches with contradictions)
```

---

## Novelty Claim

> *"VALKYRIE-Decoder is the first architecture where structured knowledge claims
> and natural language tokens are co-generated with bidirectional mutual influence,
> intra-generation conflict suppression, and query-type-aware epistemic gating —
> making hallucination prevention an intrinsic decoding property rather than a
> post-hoc correction."*
