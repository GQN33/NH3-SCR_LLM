from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from nh3map.pdf.convert_pdf_to_md import convert_pdf
from nh3map.pdf.postprocess_md import postprocess_directory


def _convert_one(pdf_path: Path, output_dir: Path) -> str:
    out = convert_pdf(pdf_path, output_dir)
    return out.name


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    parser = argparse.ArgumentParser(description="Process PDFs in parallel into Markdown and extracted images.")
    parser.add_argument("pdf_dirs", nargs="+", type=Path)
    parser.add_argument("--raw-output-dir", type=Path, required=True)
    parser.add_argument("--clean-output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = parser.parse_args()

    pdf_map: dict[str, Path] = {}
    for pdf_dir in args.pdf_dirs:
        candidates = sorted(pdf_dir.glob("*.pdf"))
        for pdf_path in candidates:
            key = pdf_path.name.lower()
            if key not in pdf_map:
                pdf_map[key] = pdf_path

    pdfs = sorted(pdf_map.values(), key=lambda p: p.name.lower())
    if not pdfs:
        joined = ", ".join(str(p) for p in args.pdf_dirs)
        raise RuntimeError(f"No PDFs found in {joined}")

    args.raw_output_dir.mkdir(parents=True, exist_ok=True)
    args.clean_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"INPUT_DIRS\t{len(args.pdf_dirs)}")
    for pdf_dir in args.pdf_dirs:
        print(f"INPUT\t{pdf_dir}")
    print(f"PDFS\t{len(pdfs)}")
    print(f"WORKERS\t{args.workers}")
    print(f"RAW_OUT\t{args.raw_output_dir}")
    print(f"CLEAN_OUT\t{args.clean_output_dir}")

    completed = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_convert_one, pdf_path, args.raw_output_dir): pdf_path for pdf_path in pdfs}
        for future in as_completed(futures):
            pdf_path = futures[future]
            try:
                name = future.result()
                completed += 1
                print(f"OK\t{completed}/{len(pdfs)}\t{pdf_path.name}\t{name}")
            except Exception as exc:
                print(f"ERROR\t{pdf_path.name}\t{exc}")

    outputs = postprocess_directory(args.raw_output_dir, args.clean_output_dir)
    print(f"POSTPROCESS_OK\t{len(outputs)}")


if __name__ == "__main__":
    main()
