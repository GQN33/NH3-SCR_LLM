from __future__ import annotations

import argparse
from pathlib import Path

from nh3map.pdf.postprocess_md import postprocess_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Postprocess Markdown files with CATDA-style cleanup.")
    parser.add_argument("src_dir", type=Path)
    parser.add_argument("--dst-dir", type=Path, required=True)
    args = parser.parse_args()

    for out_path in postprocess_directory(args.src_dir, args.dst_dir):
        print(f"OK\t{out_path.name}")


if __name__ == "__main__":
    main()
