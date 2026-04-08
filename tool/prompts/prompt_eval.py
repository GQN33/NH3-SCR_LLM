from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nh3map.prompts.eval import run_eval


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    parser = argparse.ArgumentParser(description="Evaluate NH3_MAP prompt variants on a random markdown sample.")
    parser.add_argument("--md-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--api-url", default="https://api.openai.com/v1/responses")
    parser.add_argument("--api-key")
    parser.add_argument("--sample-size", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260408)
    parser.add_argument("--max-chars", type=int, default=24000)
    parser.add_argument("--include-missing-check", action="store_true")
    args = parser.parse_args()

    summary = run_eval(
        md_dir=args.md_dir,
        out_dir=args.out_dir,
        model=args.model,
        sample_size=args.sample_size,
        seed=args.seed,
        api_key=args.api_key,
        api_url=args.api_url,
        max_chars=args.max_chars,
        include_missing_check=args.include_missing_check,
    )

    print(f"MODEL\t{summary['model']}")
    print(f"SAMPLE_SIZE\t{summary['sample_size']}")
    print(f"OUT_DIR\t{args.out_dir}")
    for name, payload in summary["profiles"].items():
        s = payload["summary"]
        print(
            f"PROFILE\t{name}\t"
            f"success={s['success']}/{s['total']}\t"
            f"avg_nodes={s['avg_nodes']:.2f}\t"
            f"avg_edges={s['avg_edges']:.2f}\t"
            f"avg_latency_s={s['avg_latency_s']:.2f}\t"
            f"catalyst_rate={s['catalyst_rate']:.2f}\t"
            f"testing_rate={s['testing_rate']:.2f}\t"
            f"characterization_rate={s['characterization_rate']:.2f}"
        )

    print("SUMMARY_JSON")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
