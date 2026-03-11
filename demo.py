"""
demo.py
=======
Complete demonstration of VALKYRIE-Decoder v2.

Sections
--------
 1. Model architecture summary
 2. Knowledge base contents
 3. Training simulation
 4. Generation with full pipeline
 5. Verified claims analysis
 6. NOVELTY #1 — Bidirectional stream gate values
 7. NOVELTY #2 — Dynamic threshold breakdown
 8. NOVELTY #3 — Conflict detection results
 9. Full gate state log
10. Parameter breakdown
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch

from models.valkyrie_decoder import ValkyrieDecoder
from models.structures import StructuredClaim
from models.conflict_detector import ConflictDetector
from training.trainer import ValkyrieTrainer
from utils.vocab import create_demo_vocabulary, vocab_size as get_vocab_size

# ── Formatting helpers ─────────────────────────────────────────────────────────
W = 68

def banner(text: str) -> None:
    print("\n" + "═" * W)
    print(f"  {text}")
    print("═" * W)

def section(n: int, title: str) -> None:
    print(f"\n{'─' * W}")
    print(f"  [{n}]  {title}")
    print(f"{'─' * W}")

def row(label: str, value, width: int = 35) -> None:
    print(f"    {label:<{width}}: {value}")


# ── Main demo ──────────────────────────────────────────────────────────────────

def demonstrate_valkyrie() -> None:

    banner("VALKYRIE-DECODER  v2  —  COMPLETE DEMONSTRATION")
    print("  Bidirectional Streams  |  Dynamic Threshold  |  Conflict Detection")

    # ── Build model ────────────────────────────────────────────────────────────
    vocab  = create_demo_vocabulary()
    vsize  = get_vocab_size(vocab)
    model  = ValkyrieDecoder(
        vocab_size = vsize,
        d_model    = 128,
        n_heads    = 4,
        n_layers   = 2,
        d_ff       = 256,
        dropout    = 0.1,
    )
    trainer = ValkyrieTrainer(model, lr=1e-3)

    # ──────────────────────────────────────────────────────────────────────────
    section(1, "Model Architecture")
    # ──────────────────────────────────────────────────────────────────────────
    pc = model.parameter_count()
    row("Vocabulary size",                vsize)
    row("Model dimension (d_model)",      128)
    row("Attention heads (n_heads)",      4)
    row("Decoder layers per stream",      2)
    row("★ Bidir cross-attn layers",     "2  ← NOVELTY #1")
    row("★ Veracity gates (dynamic)",    "2  ← NOVELTY #2")
    row("★ Conflict detectors",          "1  ← NOVELTY #3")
    print()
    row("Params — embeddings",            f"{pc['embeddings']:>10,}")
    row("Params — stream A",              f"{pc['stream_a']:>10,}")
    row("Params — stream B",              f"{pc['stream_b']:>10,}")
    row("Params — bidir cross-attn",      f"{pc['bidir_cross_attn']:>10,}")
    row("Params — veracity gates",        f"{pc['veracity_gates']:>10,}")
    row("Params — conflict detector",     f"{pc['conflict_detector']:>10,}")
    row("Params — output layer",          f"{pc['output_layer']:>10,}")
    row("TOTAL parameters",               f"{pc['total']:>10,}")

    # ──────────────────────────────────────────────────────────────────────────
    section(2, "Knowledge Base Contents")
    # ──────────────────────────────────────────────────────────────────────────
    for (s, r, o), conf in model.knowledge_base.facts.items():
        tag = "✓" if conf >= 0.95 else "~"
        print(f"    {tag}  ({s}) --[{r}]--> ({o})   conf={conf:.2f}")

    # ──────────────────────────────────────────────────────────────────────────
    section(3, "Training Simulation  (10 epochs)")
    # ──────────────────────────────────────────────────────────────────────────
    print(f"    {'Epoch':<8} {'Loss':<12} {'LM Loss':<12} "
          f"{'Truth Pen':<12} {'Conflict Pen':<14} {'Claims'}")
    print(f"    {'─'*7:<8} {'─'*10:<12} {'─'*10:<12} {'─'*10:<12} {'─'*11:<14} {'─'*6}")

    for epoch in range(1, 11):
        bi = torch.randint(3, vsize, (4, 12))
        bt = torch.randint(3, vsize, (4, 12))
        m  = trainer.train_step(bi, bt)
        print(
            f"    {epoch:<8} {m['loss']:<12.4f} {m['lm_loss']:<12.4f} "
            f"{m['truth_penalty']:<12.4f} {m['conflict_penalty']:<14.4f} "
            f"{m['claims_generated']}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    section(4, "Text Generation  (greedy decoding, max 12 tokens)")
    # ──────────────────────────────────────────────────────────────────────────
    prompts = [
        "Tell me about the Eiffel Tower",
        "Who founded Apple and Microsoft",
        "What is the capital of France",
    ]

    for prompt in prompts:
        print(f"\n    Prompt    : {prompt!r}")
        text, claims, gates = model.generate(prompt, max_length=12)
        print(f"    Generated : {text}")
        print(f"    Claims    : {len(claims)} verified, "
              f"gate {'OPEN' if any(g['gate_open'] for g in gates) else 'CLOSED'} "
              f"on last step")

    # Use the last generation for detailed analysis
    print(f"\n  (Using last prompt for detailed analysis below)")
    text, claims, gate_states = model.generate(prompts[-1], max_length=12)

    # ──────────────────────────────────────────────────────────────────────────
    section(5, "Verified Claims Analysis")
    # ──────────────────────────────────────────────────────────────────────────
    if not claims:
        print("    No claims survived the full pipeline in this run.")
        print("    (This is expected with random weights — train first)")
    else:
        verified_count   = sum(1 for c in claims if c.verified)
        unverified_count = len(claims) - verified_count
        print(f"    Total claims : {len(claims)}")
        print(f"    Verified     : {verified_count}  ({'%.0f' % (verified_count/len(claims)*100)}%)")
        print(f"    Rejected     : {unverified_count}")
        print()
        for i, c in enumerate(claims, 1):
            icon = "✓" if c.verified else "✗"
            print(f"    {icon}  Claim {i}  (layer {c.layer})")
            print(f"         Text       : {c.to_text()}")
            print(f"         Triple     : ({c.subject}) --[{c.relation}]--> ({c.object})")
            print(f"         Confidence : {c.confidence:.2f}")
            print(f"         Status     : {'VERIFIED' if c.verified else 'REJECTED'}")

    # ──────────────────────────────────────────────────────────────────────────
    section(6, "NOVELTY #1 — Bidirectional Cross-Stream Attention")
    # ──────────────────────────────────────────────────────────────────────────
    print("    Learned gate scalars controlling how much each stream")
    print("    influences the other (initialised at 0.1, learned during training):\n")
    for i, bidir in enumerate(model.bidir_cross_attn):
        gv = bidir.gate_values()
        print(f"    Layer {i}:")
        for name, val in gv.items():
            direction = "B absorbs A" if "generation" in name else "A absorbs B"
            print(f"      {direction:<20} gate = {val:.4f}")

    # Fresh forward pass for gate state inspection
    with torch.no_grad():
        test_ids = torch.randint(3, vsize, (1, 8))
        out      = model(test_ids, generate_claims=True)

    # ──────────────────────────────────────────────────────────────────────────
    section(7, "NOVELTY #2 — Dynamic Veracity Threshold")
    # ──────────────────────────────────────────────────────────────────────────
    print("    Per-layer context-sensitive gate threshold:\n")
    print(f"    {'Layer':<8} {'Query Type':<14} {'Threshold':<12} "
          f"{'Confidence':<12} {'Gate':<8} {'Reason'}")
    print(f"    {'─'*5:<8} {'─'*12:<14} {'─'*9:<12} {'─'*10:<12} {'─'*6:<8} {'─'*20}")
    for gs in out["gate_states"]:
        gate_str = "OPEN  ✓" if gs["gate_open"] else "CLOSED ✗"
        print(
            f"    {gs['layer']:<8} {gs['query_type']:<14} "
            f"{gs['dynamic_threshold']:<12.4f} {gs['confidence']:<12.4f} "
            f"{gate_str:<8} {gs['reason']}"
        )

    print("\n    Query Type → Threshold Bias:")
    print("      Factual    → 0.75  (stable facts, high bar)")
    print("      Relational → 0.60  (relationships, moderate)")
    print("      Opinion    → 0.40  (subjective, lenient)")
    print("      Temporal   → 0.85  (changes over time, strictest)")

    # ──────────────────────────────────────────────────────────────────────────
    section(8, "NOVELTY #3 — Claim Conflict Detection")
    # ──────────────────────────────────────────────────────────────────────────

    # Manually inject a known conflict to demonstrate clearly
    from models.structures import StructuredClaim
    demo_claims = [
        StructuredClaim("Apple", "founded_by", "Steve Jobs",  1.0, True,  0),
        StructuredClaim("Apple", "founded_by", "Bill Gates",  0.8, False, 0),
        StructuredClaim("Paris", "capital_of", "France",      1.0, True,  1),
        StructuredClaim("Paris", "capital_of", "Germany",     0.3, False, 1),
        StructuredClaim("Mars",  "color",      "Red",         1.0, True,  0),
    ]

    print("    Injecting demo claims for conflict demonstration:")
    for c in demo_claims:
        icon = "✓" if c.verified else "✗"
        print(f"      {icon}  {c.to_text()}  (conf={c.confidence:.2f})")

    clean, flagged, report = model.conflict_detector.detect(demo_claims)

    print(f"\n    Results:")
    print(f"      Total claims    : {report['total']}")
    print(f"      Suppressed      : {report['suppressed']}  ← both in each conflicting pair")
    print(f"      Clean / passed  : {report['clean']}")

    if report["conflicts"]:
        print(f"\n    Detected Conflicts:")
        for conf_item in report["conflicts"]:
            print(f"      ⚡  Type: {conf_item['type']}  (score={conf_item['score']:.2f},"
                  f" detected_by={conf_item['detected_by']})")
            print(f"         Claim A: {conf_item['claim_a']}")
            print(f"         Claim B: {conf_item['claim_b']}")

    if clean:
        print(f"\n    Claims that passed (no conflicts):")
        for c in clean:
            print(f"      ✓  {c.to_text()}")

    # ──────────────────────────────────────────────────────────────────────────
    section(9, "Full Gate State Log")
    # ──────────────────────────────────────────────────────────────────────────
    print(f"    (from fresh forward pass on random input)\n")
    for gs in out["gate_states"]:
        status = "🟢 OPEN  " if gs["gate_open"] else "🔴 CLOSED"
        print(f"    Layer {gs['layer']}  {status}")
        print(f"      Query type        : {gs['query_type']}")
        print(f"      Dynamic threshold : {gs['dynamic_threshold']:.4f}")
        print(f"      KB confidence     : {gs['confidence']:.4f}")
        print(f"      Gate scalar       : {gs['gate_value']:.4f}")
        print(f"      Decision reason   : {gs['reason']}")

    if out.get("conflict_reports"):
        print(f"\n    Conflict reports from this pass:")
        for rpt in out["conflict_reports"]:
            print(f"      Layer {rpt.get('layer','?')}: "
                  f"{rpt['suppressed']} suppressed, {rpt['clean']} clean")

    # ──────────────────────────────────────────────────────────────────────────
    section(10, "Feature Checklist")
    # ──────────────────────────────────────────────────────────────────────────
    features = [
        ("✓", "base",    "Dual-stream transformer decoder (A + B)"),
        ("✓", "base",    "StructuredClaim extraction (subject, relation, object)"),
        ("✓", "base",    "Knowledge base fact verification"),
        ("✓", "base",    "Confidence scoring per claim"),
        ("✓", "base",    "Three-term training loss (LM + truth + conflict)"),
        ("★", "NEW #1",  "Bidirectional Cross-Stream Attention (A ↔ B)"),
        ("★", "NEW #2",  "Dynamic Veracity Threshold (query-type + depth aware)"),
        ("★", "NEW #3",  "Claim Conflict Detection (object / relation / symmetric)"),
        ("✓", "base",    "ValkyrieWithMemory — persistent fact caching"),
        ("✓", "base",    "AdvancedVeracityGate — attention-based claim extraction"),
    ]
    print(f"    {'Icon':<5} {'Version':<10} Description")
    print(f"    {'─'*4:<5} {'─'*8:<10} {'─'*40}")
    for icon, ver, desc in features:
        print(f"    {icon:<5} {ver:<10} {desc}")

    banner("DEMONSTRATION COMPLETE")
    print("  Run:  python main.py --interactive   to try your own prompts")
    print("═" * W)


if __name__ == "__main__":
    demonstrate_valkyrie()
