"""
main.py
=======
Entry point for VALKYRIE-Decoder v2.

Usage
-----
  python main.py                  # run automated demo
  python main.py --interactive    # demo + interactive prompt mode
  python main.py --interactive --no-demo   # skip demo, go straight to interactive
  python main.py --test           # quick sanity check (no full demo)
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

from models.valkyrie_decoder import ValkyrieDecoder
from utils.vocab import create_demo_vocabulary, vocab_size as get_vocab_size
from demo.demo import demonstrate_valkyrie


# ── Model factory ─────────────────────────────────────────────────────────────

def build_model(d_model: int = 128, n_layers: int = 2) -> ValkyrieDecoder:
    """Build a demo-sized ValkyrieDecoder."""
    vocab = create_demo_vocabulary()
    vsize = get_vocab_size(vocab)
    return ValkyrieDecoder(
        vocab_size = vsize,
        d_model    = d_model,
        n_heads    = 4,
        n_layers   = n_layers,
        d_ff       = d_model * 2,
        dropout    = 0.1,
    )


# ── Interactive mode ──────────────────────────────────────────────────────────

def interactive_mode(model: ValkyrieDecoder) -> None:
    W = 68
    print("\n" + "═" * W)
    print("  INTERACTIVE MODE")
    print("  Type a prompt and press Enter.")
    print("  Commands:  'kb'=show knowledge base  'quit'=exit")
    print("═" * W)

    while True:
        try:
            prompt = input("\n  Your prompt › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting interactive mode.")
            break

        if not prompt:
            continue

        if prompt.lower() == "quit":
            print("  Goodbye.")
            break

        if prompt.lower() == "kb":
            print(model.knowledge_base.summary())
            continue

        # Generate
        print(f"\n  Generating...")
        text, claims, gate_states = model.generate(prompt, max_length=15)

        print(f"\n  Generated text : {text}")

        # Gate summary
        print(f"\n  Gate summary ({len(gate_states)} layers):")
        for gs in gate_states:
            status = "OPEN  ✓" if gs["gate_open"] else "CLOSED ✗"
            print(
                f"    Layer {gs['layer']}: {status:<10} "
                f"type={gs['query_type']:<12} "
                f"threshold={gs['dynamic_threshold']:.3f}  "
                f"conf={gs['confidence']:.3f}"
            )

        # Claims
        if claims:
            print(f"\n  Verified claims ({len(claims)}):")
            for c in claims[-5:]:
                icon = "✓" if c.verified else "✗"
                print(f"    {icon}  {c.to_text()}  "
                      f"(conf={c.confidence:.2f}, layer={c.layer})")
        else:
            print("\n  No claims passed the full pipeline.")


# ── Quick sanity test ─────────────────────────────────────────────────────────

def quick_test() -> None:
    print("Running sanity check...")
    model = build_model()
    vocab = create_demo_vocabulary()
    vsize = get_vocab_size(vocab)

    # Forward pass
    dummy_input = torch.randint(3, vsize, (2, 10))
    out = model(dummy_input, generate_claims=True)

    assert out["logits"].shape == (2, 10, vsize), "Logits shape mismatch"
    assert "claims"           in out
    assert "gate_states"      in out
    assert "conflict_reports" in out
    assert "flagged_claims"   in out

    print(f"  ✓  Forward pass OK  — logits shape: {tuple(out['logits'].shape)}")
    print(f"  ✓  Gate states     : {len(out['gate_states'])} layers")
    print(f"  ✓  Claims          : {len(out['claims'])}")
    print(f"  ✓  Flagged         : {len(out['flagged_claims'])}")

    # Generate
    text, claims, gates = model.generate("Test prompt", max_length=5)
    print(f"  ✓  Generation OK   : {text}")
    print("All checks passed.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="VALKYRIE-Decoder v2 — Veracity-Gated Dual-Stream Transformer"
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="Enter interactive prompt mode after the demo."
    )
    parser.add_argument(
        "--no-demo", action="store_true",
        help="Skip the automated demo (use with --interactive)."
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run a quick sanity check and exit."
    )
    args = parser.parse_args()

    if args.test:
        quick_test()
        return

    if not args.no_demo:
        demonstrate_valkyrie()

    if args.interactive:
        model = build_model()
        interactive_mode(model)


if __name__ == "__main__":
    main()
