from __future__ import annotations

import argparse
from pathlib import Path

from nh3map.pdf.convert_pdf_to_md import convert_from_manifest, sample_and_convert


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert sample PDFs to Markdown and extract images.")
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--reuse-manifest", action="store_true")
    args = parser.parse_args()

    if args.reuse_manifest and args.manifest.exists():
        outputs = convert_from_manifest(args.pdf_dir, args.output_dir, args.manifest)
    else:
        outputs = sample_and_convert(args.pdf_dir, args.output_dir, args.manifest, args.sample_size)

    for output in outputs:
        print(f"OK\t{output.name}")


if __name__ == "__main__":
    main()
