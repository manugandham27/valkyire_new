# VALKYRIE-50K: Structured Knowledge Facts for LLM Hallucination Detection

## Overview
A comprehensive dataset of **50,000 structured knowledge samples** designed for training and evaluating hallucination detection and fact verification systems in Large Language Models (LLMs).

This dataset was created as part of the **VALKYRIE-Decoder** project — a decoder-integrated neuro-symbolic gating framework for hallucination mitigation in LLMs.

## Dataset Structure

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Unique sequential identifier (1–50000) |
| `text` | string | Human-readable natural language claim |
| `subject` | string | Entity subject of the knowledge triple |
| `relation` | string | Relationship type connecting subject to object |
| `object` | string | Entity object of the knowledge triple |
| `confidence` | float | Confidence score (0.10–1.00) |
| `label` | string | `TRUE` (verified fact) or `FALSE` (hallucination) |

## Label Distribution

| Label | Count | Percentage |
|-------|-------|------------|
| TRUE (Verified Facts) | 49,950 | 99.90% |
| FALSE (Hallucinations) | 50 | 0.10% |

## Knowledge Domains

The dataset covers **10+ knowledge domains** with 741 curated real-world facts:

| Domain | Relation Types | Sample Count | Examples |
|--------|---------------|-------------|----------|
| Geography | `capital_of`, `located_in` | 157 | Paris → capital_of → France |
| Technology | `founded_by`, `located_in` | 100 | Apple → founded_by → Steve Jobs |
| Science | `discovered`, `is` | 80 | Einstein → discovered → Relativity |
| History | `discovered`, `founded_by` | 20 | Columbus → discovered → Americas |
| Biology | `is`, `located_in` | 20 | Blue Whale → is → Largest Animal |
| Languages | `is` | 20 | English → is → Language Of United Kingdom |
| Sports | `located_in`, `is` | 20 | Premier League → located_in → England |
| Food & Cuisine | `located_in` | 20 | Sushi → located_in → Japan |
| Universities | `located_in` | 28 | Harvard → located_in → Cambridge |
| Currencies | `is` | 20 | Dollar → is → Currency Of United States |
| Rivers & Water Bodies | `located_in`, `is` | 33 | Nile River → located_in → Egypt |
| Mountains | `located_in` | 20 | Mount Everest → located_in → Nepal |
| Inventions | `founded_by` | 25 | Telephone → founded_by → Alexander Graham Bell |
| Computing & AI | `founded_by` | 25 | Python → founded_by → Guido Van Rossum |
| Architecture | `located_in` | 20 | Empire State Building → located_in → New York |
| Organizations | `located_in`, `is` | 20 | United Nations → located_in → New York |
| Literature | `founded_by` | 20 | Harry Potter → founded_by → J.K. Rowling |
| Automotive | `founded_by` | 20 | Ferrari → founded_by → Enzo Ferrari |
| Medicine | `is` | 20 | Insulin → is → Diabetes Treatment |
| Astronomy | `is`, `color`, `located_in` | 20 | Mars → color → Red |
| Population | `population_of` | 25 | Tokyo → population_of → 37 Million |

## Relation Types

| Relation | Count | Description |
|----------|-------|-------------|
| `is_related_to` | 49,259 | Synthetic padding relations |
| `located_in` | 311 | Geographic/organizational location |
| `founded_by` | 150 | Creator/founder relationship |
| `is` | 135 | Classification/identity |
| `capital_of` | 67 | Capital city relationship |
| `discovered` | 51 | Scientific/exploration discovery |
| `population_of` | 25 | City population data |
| `color` | 2 | Physical color attribute |

## False Claims (Hallucination Examples)

The dataset includes 50 deliberately false claims for adversarial training:

```
Paris → capital_of → Germany (FALSE, conf=0.10)
Apple → founded_by → Bill Gates (FALSE, conf=0.10)  
Mars → color → Blue (FALSE, conf=0.10)
Einstein → discovered → Penicillin (FALSE, conf=0.10)
```

## Use Cases

- **Hallucination Detection**: Train binary classifiers to distinguish TRUE facts from FALSE claims
- **Fact Verification**: Build knowledge-graph-based verification pipelines
- **Knowledge Base Construction**: Seed structured knowledge bases with verified triples
- **NLP Benchmarking**: Evaluate LLM factual accuracy against ground truth
- **Neuro-Symbolic AI**: Train hybrid systems combining neural and symbolic reasoning

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{gandham2026valkyrie50k,
  title={VALKYRIE-50K: Structured Knowledge Facts for LLM Hallucination Detection},
  author={Gandham, Manu},
  year={2026},
  publisher={Kaggle},
  url={https://www.kaggle.com/datasets/manugandham27/valkyrie-50k-hallucination-detection}
}
```

## Related Work

This dataset was developed as part of the VALKYRIE-Decoder research project:
- **Paper**: "VALKYRIE-Decoder: A Decoder-Integrated Neuro-Symbolic Gating Framework for Hallucination Mitigation in LLMs"
- **GitHub**: [github.com/manugandham27/valkyire_new](https://github.com/manugandham27/valkyire_new)

## License

This dataset is released under the [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) license.
