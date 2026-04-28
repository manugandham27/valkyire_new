# Graph Report - valkyire_new  (2026-04-23)

## Corpus Check
- 29 files · ~89,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 242 nodes · 470 edges · 14 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]

## God Nodes (most connected - your core abstractions)
1. `StructuredClaim` - 55 edges
2. `KnowledgeBase` - 31 edges
3. `ValkyrieDecoder` - 29 edges
4. `VeracityGate` - 20 edges
5. `MultiHeadAttention` - 20 edges
6. `ConflictDetector` - 17 edges
7. `BidirectionalCrossStreamAttention` - 16 edges
8. `demonstrate_valkyrie()` - 15 edges
9. `DynamicVeracityThreshold` - 15 edges
10. `ValkyrieWithMemory` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Same as train_step but without gradient updates.` --uses--> `ValkyrieDecoder`  [INFERRED]
  training/trainer.py → models/valkyrie_decoder.py
- `main()` --calls--> `build_large_dataset()`  [INFERRED]
  export_dataset.py → utils/large_dataset.py
- `main()` --calls--> `create_demo_vocabulary()`  [INFERRED]
  generate_accuracy_graph.py → utils/vocab.py
- `main()` --calls--> `ValkyrieDecoder`  [INFERRED]
  generate_accuracy_graph.py → models/valkyrie_decoder.py
- `main()` --calls--> `evaluate_step()`  [INFERRED]
  generate_accuracy_graph.py → training/trainer.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (21): bidirectional_stream.py ======================= NOVELTY #1 — Bidirectional Cross, Mutual cross-attention between knowledge stream (A) and generation     stream (B, Apply bidirectional cross-stream attention.          Returns         -------, DynamicVeracityThreshold, QueryTypeClassifier, dynamic_threshold.py ==================== NOVELTY #2 — Dynamic Veracity Threshol, Compute the dynamic threshold.          Parameters         ----------         st, Return the dominant query type label for the first batch sample. (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (22): Return current learned gate values for monitoring., Scans all pairs of generated claims for logical contradictions.     Suppresses B, Same subject + relation, different objects → contradiction., Same subject + object, mutually exclusive relations., A→B and B→A for an asymmetric relation., banner(), demonstrate_valkyrie(), demo.py ======= Complete demonstration of VALKYRIE-Decoder v2.  Sections ------- (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (18): BidirectionalCrossStreamAttention, ConflictDetector, PositionalEncoding, transformer_blocks.py ===================== Reusable transformer building blocks, Standard transformer encoder/decoder block.      Structure (post-norm):, Sinusoidal positional encoding (Vaswani et al., 2017).     Adds position informa, Add positional encoding to *x* of shape (B, T, d_model)., TransformerBlock (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (10): ClaimEmbedder, _object_conflict(), conflict_detector.py ==================== NOVELTY #3 — Claim Conflict Detection, Return a (1, embed_dim) embedding for *claim*., Scan all claim pairs for conflicts.          Parameters         ----------, Embeds a StructuredClaim into a fixed-size vector.     Uses learned lookup table, _relation_conflict(), _symmetric_conflict() (+2 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (20): decode(), _fuzzy_match(), get_entity_facts(), wikidata_api.py =============== Query Wikidata's free SPARQL endpoint to verify, Smart entity search that uses the relation context to disambiguate.     E.g. 'Ap, For a given entity QID, check if any of the given properties     have a value wh, Verify a (subject, relation, object) triple against Wikidata.      Returns     -, Retrieve key facts about an entity from Wikidata.     Returns list of (relation, (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (14): Return all (relation, object, confidence) entries for *subject*.         Uses ca, build_model(), extract_claims_from_text(), interactive_mode(), main(), quick_test(), main.py ======= Entry point for VALKYRIE-Decoder v2.  Usage -----   python main., Parse natural language text into StructuredClaims and verify against KB.     Ret (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (8): KnowledgeBase, _norm(), knowledge_base.py ================= Hybrid knowledge base: local fact store + li, Remove a fact if present. Returns True if it existed., Return all (subject, relation, confidence) entries for *obj*., Stores ground-truth facts and verifies StructuredClaims against them.      Each, Check whether *claim* exists in the knowledge base.          Returns         ---, Hybrid verification: local KB first, then Wikidata API.          Returns (verifi

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (10): main(), export_dataset.py ================= Export the VALKYRIE 50,000-sample dataset to, Dynamically add a new fact., build_large_dataset(), DataSample, large_dataset.py ================ Comprehensive knowledge dataset for VALKYRIE-D, One fact sample for the knowledge base., Return DataSample objects covering diverse knowledge domains up to target_size. (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.31
Nodes (9): build(), fig_block(), H1(), H2(), M(), P(), generate_springer_paper.py  v1 ========================== Generates a Springer-s, S() (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (10): build(), fig_block(), H1(), H2(), M(), P(), generate_ieee_paper.py  v3 ========================== Scientifically rigorous IE, rule() (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.22
Nodes (1): generate_paper_figures.py ========================= Generates all figures for th

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (2): FeedForward, Position-wise feed-forward network with GELU activation.     Applied independent

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): clean_html(), parse_and_convert()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): paper_content.py — Revised content for the VALKYRIE-Decoder IEEE paper. v3: Scie

## Knowledge Gaps
- **42 isolated node(s):** `export_dataset.py ================= Export the VALKYRIE 50,000-sample dataset to`, `generate_springer_paper.py  v1 ========================== Generates a Springer-s`, `generate_paper_figures.py ========================= Generates all figures for th`, `generate_ieee_paper.py  v3 ========================== Scientifically rigorous IE`, `paper_content.py — Revised content for the VALKYRIE-Decoder IEEE paper. v3: Scie` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 10`** (9 nodes): `fig1_training_curves()`, `fig2_comparative_bar()`, `fig3_threshold_analysis()`, `fig4_ablation_study()`, `fig5_confusion_matrix()`, `fig6_gate_scalars()`, `fig7_kb_coverage()`, `generate_paper_figures.py`, `generate_paper_figures.py ========================= Generates all figures for th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (7 nodes): `FeedForward`, `.forward()`, `.__init__()`, `.__init__()`, `.__init__()`, `Position-wise feed-forward network with GELU activation.     Applied independent`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (3 nodes): `clean_html()`, `parse_and_convert()`, `export_latex.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `paper_content.py`, `paper_content.py — Revised content for the VALKYRIE-Decoder IEEE paper. v3: Scie`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StructuredClaim` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.247) - this node is a cross-community bridge._
- **Why does `KnowledgeBase` connect `Community 6` to `Community 0`, `Community 1`, `Community 2`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `ValkyrieDecoder` connect `Community 2` to `Community 1`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `StructuredClaim` (e.g. with `main.py ======= Entry point for VALKYRIE-Decoder v2.  Usage -----   python main.` and `Load all TRUE facts from large_dataset into the model's KB.     Returns the numb`) actually correct?**
  _`StructuredClaim` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `KnowledgeBase` (e.g. with `StructuredClaim` and `VeracityGate`) actually correct?**
  _`KnowledgeBase` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `ValkyrieDecoder` (e.g. with `main.py ======= Entry point for VALKYRIE-Decoder v2.  Usage -----   python main.` and `Load all TRUE facts from large_dataset into the model's KB.     Returns the numb`) actually correct?**
  _`ValkyrieDecoder` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `VeracityGate` (e.g. with `StructuredClaim` and `KnowledgeBase`) actually correct?**
  _`VeracityGate` has 14 INFERRED edges - model-reasoned connections that need verification._