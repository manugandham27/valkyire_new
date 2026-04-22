"""
export_dataset.py
=================
Export the VALKYRIE 50,000-sample dataset to CSV format.
"""

import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.large_dataset import build_large_dataset

def main():
    print("Building dataset...")
    samples = build_large_dataset()
    print(f"Total samples: {len(samples)}")

    output_path = os.path.join(os.path.dirname(__file__), "data", "valkyrie_dataset_50k.csv")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "subject", "relation", "object", "confidence", "label"])
        for idx, s in enumerate(samples):
            writer.writerow([
                idx + 1,
                s.text,
                s.subject,
                s.relation,
                s.obj,
                f"{s.confidence:.2f}",
                "TRUE" if s.label else "FALSE",
            ])

    print(f"✓ Exported {len(samples)} samples to: {output_path}")

    # Print summary stats
    true_count = sum(1 for s in samples if s.label)
    false_count = sum(1 for s in samples if not s.label)
    relations = {}
    for s in samples:
        relations[s.relation] = relations.get(s.relation, 0) + 1

    print(f"\n  Summary:")
    print(f"    TRUE  facts:  {true_count}")
    print(f"    FALSE claims: {false_count}")
    print(f"    Relations breakdown:")
    for rel, count in sorted(relations.items(), key=lambda x: -x[1]):
        print(f"      {rel:<20} {count:>6}")

if __name__ == "__main__":
    main()
