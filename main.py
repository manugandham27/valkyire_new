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
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

from models.valkyrie_decoder import ValkyrieDecoder
from models.structures import StructuredClaim
from utils.vocab import create_demo_vocabulary, vocab_size as get_vocab_size, encode, decode
from demo.demo import demonstrate_valkyrie


# ── Load full KB from large dataset ──────────────────────────────────────────

def load_full_knowledge_base(model: ValkyrieDecoder) -> int:
    """
    Load all TRUE facts from large_dataset into the model's KB.
    Returns the number of facts loaded.
    """
    try:
        from utils.large_dataset import build_large_dataset
        samples = build_large_dataset()
        added = 0
        for s in samples:
            if s.is_true() and s.has_triple():
                model.knowledge_base.add_fact(
                    s.subject, s.relation, s.obj, s.confidence
                )
                added += 1
        return added
    except Exception as e:
        print(f"  (Could not load large dataset: {e})")
        return 0


# ── Smart claim extractor from raw text ──────────────────────────────────────

# Maps common phrases to (regex, relation, obj_transform).
# obj_transform: None → use group(2) as-is.
#                "Currency Of {2}" → build the object from the format string
#                                     where {2} is replaced by group(2).
# ORDER MATTERS — more specific patterns go first; the greedy "X is Y" is last.
_RELATION_PATTERNS = [
    # ── Authorship / creation ────────────────────────────────────────
    (r"(.+?)\s+was written by\s+(.+)",                       "founded_by", None),
    (r"(.+?)\s+was invented by\s+(.+)",                      "founded_by", None),
    (r"(.+?)\s+was created by\s+(.+)",                       "founded_by", None),
    (r"(.+?)\s+was developed by\s+(.+)",                     "founded_by", None),
    (r"(.+?)\s+was designed by\s+(.+)",                      "founded_by", None),
    (r"(.+?)\s+was built by\s+(.+)",                         "founded_by", None),
    (r"(.+?)\s+was founded by\s+(.+)",                       "founded_by", None),
    (r"(.+?)\s+was discovered by\s+(.+)",                    "discovered", None),

    # ── Discovery (active voice) ─────────────────────────────────────
    (r"(.+?)\s+discovered\s+(.+)",                           "discovered", None),
    (r"(.+?)\s+invented\s+(.+)",                             "founded_by", None),
    (r"(.+?)\s+created\s+(.+)",                              "founded_by", None),
    (r"(.+?)\s+founded\s+(.+)",                              "founded_by", None),
    (r"(.+?)\s+wrote\s+(.+)",                                "founded_by", None),

    # ── Origin / location (specific) ─────────────────────────────────
    (r"(.+?)\s+originates from\s+(.+)",                      "located_in", None),
    (r"(.+?)\s+comes from\s+(.+)",                           "located_in", None),
    (r"(.+?)\s+was born in\s+(.+)",                          "located_in", None),
    (r"(.+?)\s+is (?:located|situated|based) in\s+(.+)",     "located_in", None),

    # ── Capital ──────────────────────────────────────────────────────
    (r"(.+?)\s+is the capital of\s+(.+)",                    "capital_of", None),
    (r"(.+?)\s+is (?:the )?capital of\s+(.+)",               "capital_of", None),

    # ── Population ───────────────────────────────────────────────────
    (r"(.+?)\s+has a population of\s+(.+)",                  "population_of", None),

    # ── "X is the currency/language of Y" → object = "Currency Of Y" ─
    (r"(.+?)\s+is the currency of\s+(.+)",                   "is", "Currency Of {2}"),
    (r"(.+?)\s+is the language of\s+(.+)",                   "is", "Language Of {2}"),

    # ── Superlative: "X is largest/smallest/... Y" ───────────────────
    (r"(.+?)\s+is (?:the )?(largest|smallest|tallest|fastest|hottest|coldest|closest|farthest|nearest|oldest|youngest)\s+(.+)", "is", "{adj} {3}"),

    # ── Other specific ───────────────────────────────────────────────
    (r"(.+?)\s+is known as\s+(.+)",                          "is", None),
    (r"(.+?)\s+is (?:\w+ )?(?:in )?color\s+(.+)",           "color", None),
    (r"(.+?)\s+plays in\s+(.+)",                             "located_in", None),
    (r"(.+?)\s+is in\s+(.+)",                                "located_in", None),

    # ── Generic catch-all "X is (a/an/the) Y" — MUST be LAST ────────
    (r"(.+?)\s+is (?:a |an |the )?\s*(.+)",                  "is", None),
]

def extract_claims_from_text(text: str, kb) -> list:
    """
    Parse natural language text into StructuredClaims and verify against KB.
    Returns list of (claim_text, relation, subject, obj, verified, confidence).
    """
    results = []
    text = text.strip().rstrip(".")

    for entry in _RELATION_PATTERNS:
        pattern, relation, obj_transform = entry
        m = re.match(pattern, text, re.IGNORECASE)
        if m:
            subject = m.group(1).strip().title()

            # Build the object string
            if obj_transform is None:
                obj = m.group(2).strip().title()
            elif "{adj}" in obj_transform:
                # Superlative pattern: group(2) = adjective, group(3) = noun
                adj = m.group(2).strip().title()
                noun = m.group(3).strip().title()
                obj = f"{adj} {noun}"
            else:
                # Format-string transform, e.g. "Currency Of {2}"
                raw_obj = m.group(2).strip().title()
                obj = obj_transform.replace("{2}", raw_obj)

            # Try KB lookup (local first, then Wikidata API)
            verified, conf, source = kb.verify_triple(subject, relation, obj)

            # Also try fuzzy: search all facts for subject
            if not verified:
                subject_facts = kb.search_subject(subject)
                for (rel, ob, c) in subject_facts:
                    if ob.lower() == obj.lower():
                        verified, conf, source = True, c, "local"
                        relation = rel
                        break

            # Try reverse: maybe the subject/object are swapped in the KB
            if not verified:
                obj_facts = kb.search_by_object(obj)
                for (subj_found, rel, c) in obj_facts:
                    if subj_found.lower() == subject.lower():
                        verified, conf, source = True, c, "local"
                        relation = rel
                        break

            results.append({
                "text":     text,
                "subject":  subject,
                "relation": relation,
                "object":   obj,
                "verified": verified,
                "confidence": conf if verified else 0.1,
                "source":   source if verified else "",
            })
            break   # use first matching pattern

    # If no pattern matched, do a broad KB search for multi-word + single-word
    if not results:
        # Try progressively shorter multi-word chunks
        title_text = text.title()
        words = title_text.split()
        found = False

        # Try multi-word spans (longest first)
        for span_len in range(min(len(words), 5), 0, -1):
            if found:
                break
            for start_idx in range(len(words) - span_len + 1):
                candidate = " ".join(words[start_idx : start_idx + span_len])
                facts = kb.search_subject(candidate)
                if facts:
                    rel, obj, conf = facts[0]
                    results.append({
                        "text":     text,
                        "subject":  candidate,
                        "relation": rel,
                        "object":   obj,
                        "source":   "local",
                        "verified": True,
                        "confidence": conf,
                    })
                    found = True
                    break

    return results


# ── Model factory ─────────────────────────────────────────────────────────────

def build_model(d_model: int = 128, n_layers: int = 2) -> ValkyrieDecoder:
    """Build a demo-sized ValkyrieDecoder and load the full KB."""
    vocab = create_demo_vocabulary()
    vsize = get_vocab_size(vocab)
    model = ValkyrieDecoder(
        vocab_size = vsize,
        d_model    = d_model,
        n_heads    = 4,
        n_layers   = n_layers,
        d_ff       = d_model * 2,
        dropout    = 0.1,
    )
    return model


# ── Interactive mode ──────────────────────────────────────────────────────────

def interactive_mode(model: ValkyrieDecoder) -> None:
    W = 68
    vocab = create_demo_vocabulary()

    # Load full knowledge base
    print("\n  Loading knowledge base...")
    added = load_full_knowledge_base(model)
    api_status = "✓ ONLINE" if model.knowledge_base.use_api else "✗ OFFLINE"
    print(f"  ✓  Local KB ready  — {len(model.knowledge_base)} facts loaded")
    print(f"  🌐  Wikidata API   — {api_status}")

    print("\n" + "═" * W)
    print("  INTERACTIVE MODE  — VALKYRIE-Decoder v2")
    print("  Type any sentence and press Enter to verify it.")
    print(f"  Sources: LOCAL KB ({len(model.knowledge_base.facts)} curated facts) + WIKIDATA API (100M+ facts)")
    print("  Commands:")
    print("    kb       → show all facts in knowledge base")
    print("    stats    → show KB statistics by domain")
    print("    quit     → exit")
    print("═" * W)

    while True:
        try:
            prompt = input("\n  Your prompt › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            break

        if not prompt:
            continue

        if prompt.lower() == "quit":
            print("  Goodbye.")
            break

        if prompt.lower() == "kb":
            facts = list(model.knowledge_base.facts.items())
            print(f"\n  Knowledge Base — {len(facts)} facts (showing first 20):")
            for (s, r, o), conf in facts[:20]:
                print(f"    ({s}) --[{r}]--> ({o})  conf={conf:.2f}")
            if len(facts) > 20:
                print(f"    ... and {len(facts)-20} more. Type 'kb all' to see all.")
            continue

        if prompt.lower() == "kb all":
            print(f"\n  Knowledge Base — {len(model.knowledge_base.facts)} facts:")
            for (s, r, o), conf in model.knowledge_base.facts.items():
                print(f"    ({s}) --[{r}]--> ({o})  conf={conf:.2f}")
            continue

        if prompt.lower() == "stats":
            facts = list(model.knowledge_base.facts.items())
            domains = {}
            for (s, r, o), conf in facts:
                # Group by relation type
                domains[r] = domains.get(r, 0) + 1
            print(f"\n  KB Stats — {len(facts)} total facts:")
            for rel, count in sorted(domains.items(), key=lambda x: -x[1])[:15]:
                bar = "█" * (count // 3)
                print(f"    {rel:<20} {count:>4}  {bar}")
            continue

        # ── Step 1: Extract and verify claims from the text ──────────────
        print(f"\n  Analysing: \"{prompt}\"")
        print(f"  {'─' * 60}")

        claims_found = extract_claims_from_text(prompt, model.knowledge_base)

        if claims_found:
            print(f"\n  Claim Verification Results:")
            for c in claims_found:
                src     = c.get("source", "")
                if c["verified"]:
                    src_badge = f"[{src.upper()}]" if src else ""
                    icon = f"✓  VERIFIED  {src_badge}"
                else:
                    icon = "✗  NOT FOUND"
                conf_str = f"conf={c['confidence']:.2f}" if c["verified"] else "conf=0.00"
                print(f"    {icon}  ({c['subject']}) --[{c['relation']}]--> ({c['object']})  {conf_str}")
                if c["verified"]:
                    # Show related facts from KB
                    related = model.knowledge_base.search_subject(c["subject"])
                    if len(related) > 1:
                        print(f"             Related facts about '{c['subject']}':")
                        for rel, obj, conf in related[:3]:
                            print(f"               → [{rel}] → {obj}  (conf={conf:.2f})")
                else:
                    # Check if the model knows the TRUE object for this subject and relation
                    subject_facts = model.knowledge_base.search_subject(c["subject"])
                    correction_found = False
                    
                    for rel, obj, conf in subject_facts:
                        if rel == c["relation"]:
                            if not correction_found:
                                print(f"             💡 CORRECTION: {c['subject']} --[{rel}]--> {obj} (not '{c['object']}')")
                            correction_found = True
                    
                    # If we couldn't find a direct correction, fallback to typo suggestions
                    if not correction_found:
                        print(f"             ⚠  Could not verify '{c['subject']}' --[{c['relation']}]-->.")
                        words = prompt.title().split()
                        suggestions_printed = 0
                        spelling_mistake_notified = False
                        
                        for w in words:
                            if len(w) <= 3: continue  # Skip small words like "Is", "The", "In"
                            facts = model.knowledge_base.search_subject(w)
                            if facts and suggestions_printed < 2:
                                if not spelling_mistake_notified:
                                    print(f"             📝 It looks like there might be a spelling mistake in your subject!")
                                    spelling_mistake_notified = True
                                print(f"             💡 Did you mean '{w}'? Known facts:")
                                for rel, obj, conf in facts[:2]:
                                    print(f"               → [{rel}] → {obj}  (conf={conf:.2f})")
                                suggestions_printed += 1
        else:
            print(f"\n  ⚠  Could not parse a claim from this input.")
            print(f"     Try: 'Paris is the capital of France'")
            print(f"     Try: 'Apple was founded by Steve Jobs'")

        # ── Step 2: Run through neural pipeline ──────────────────────────
        print(f"\n  Neural Pipeline (gate states):")
        tokens = encode(prompt, vocab)
        if not tokens:
            tokens = [3]  # UNK
        input_tensor = torch.tensor([tokens], dtype=torch.long)

        model.eval()
        with torch.no_grad():
            out = model(input_tensor, generate_claims=True)

        gate_states = out["gate_states"]
        # Show one gate state per layer (deduplicated)
        seen_layers = set()
        shown = 0
        for gs in gate_states:
            layer = gs["layer"]
            if layer not in seen_layers:
                seen_layers.add(layer)
                status = "OPEN  ✓" if gs["gate_open"] else "CLOSED ✗"
                print(
                    f"    Layer {layer}: {status:<10} "
                    f"type={gs['query_type']:<12} "
                    f"threshold={gs['dynamic_threshold']:.3f}  "
                    f"conf={gs['confidence']:.3f}"
                )
                shown += 1
            if shown >= 4:
                break

        # Show conflict reports
        conflict_reports = out.get("conflict_reports", [])
        if conflict_reports:
            total_suppressed = sum(r.get("suppressed", 0) for r in conflict_reports)
            if total_suppressed > 0:
                print(f"\n  ⚡ Conflict detector suppressed {total_suppressed} contradicting claims")

        # ── Step 3: Final verdict ─────────────────────────────────────────
        print(f"\n  {'─' * 60}")
        if claims_found and any(c["verified"] for c in claims_found):
            verified_count = sum(1 for c in claims_found if c["verified"])
            print(f"  ✅  VERDICT: {verified_count}/{len(claims_found)} claim(s) VERIFIED in Knowledge Base")
        elif claims_found:
            print(f"  ❌  VERDICT: Claim NOT found in Knowledge Base — potential hallucination")
        else:
            print(f"  ⚠   VERDICT: Could not extract a verifiable claim from input")


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
    parser.add_argument(
        "--offline", action="store_true",
        help="Disable Wikidata API queries (use local KB only)."
    )
    args = parser.parse_args()

    if args.test:
        quick_test()
        return

    if not args.no_demo:
        demonstrate_valkyrie()

    if args.interactive:
        model = build_model()
        if args.offline:
            model.knowledge_base.use_api = False
        interactive_mode(model)
    elif not args.test:
        # After demo, drop into interactive automatically
        model = build_model()
        if args.offline:
            model.knowledge_base.use_api = False
        interactive_mode(model)


if __name__ == "__main__":
    main()