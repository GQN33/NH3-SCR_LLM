from __future__ import annotations

import re
from pathlib import Path


PAGE_NOISE_PATTERNS = [
    re.compile(r"^Frontiers in .+ frontiersin\.org \d+$", re.IGNORECASE),
    re.compile(r"^[A-Z][A-Za-z .&-]+(?:Journal|Chemistry|Catalysis|Advances|Research).*\d{1,4}$"),
    re.compile(r"^[A-Z][a-z]+ et al\. .+10\.\d{4,9}/", re.IGNORECASE),
    re.compile(r"^PUBLISHED \d{1,2} .+$", re.IGNORECASE),
    re.compile(r"^RECEIVED \d{1,2} .+$", re.IGNORECASE),
    re.compile(r"^ACCEPTED \d{1,2} .+$", re.IGNORECASE),
    re.compile(r"^DOI 10\.\d{4,9}/.+$", re.IGNORECASE),
    re.compile(r"^TYPE .+$", re.IGNORECASE),
    re.compile(r"^OPEN ACCESS$", re.IGNORECASE),
    re.compile(r"^SPECIALTY SECTION .+$", re.IGNORECASE),
    re.compile(r"^CITATION .+$", re.IGNORECASE),
    re.compile(r"^COPYRIGHT .+$", re.IGNORECASE),
    re.compile(r"^Received for review, .+$", re.IGNORECASE),
    re.compile(r"^[A-Z][a-z]+ et al\. 10\.\d{4,9}/.+$", re.IGNORECASE),
]

FIGURE_PATTERNS = [
    re.compile(r"^(?:and )?(?:Figure|Fig\.?|Scheme)\s+[A-Z]?\d+[A-Za-z]?(?:[.:, ].*)?$", re.IGNORECASE),
    re.compile(r"^Reproduced with permission .*$", re.IGNORECASE),
    re.compile(r"^Copyright \d{4}.*$", re.IGNORECASE),
]

METADATA_LINE_PATTERNS = [
    re.compile(r"^(?:EDITED BY|REVIEWED BY|SPECIALTY SECTION|COPYRIGHT)\b", re.IGNORECASE),
    re.compile(r"^\*?CORRESPONDENCE\b", re.IGNORECASE),
    re.compile(r"^(?:RECEIVED|ACCEPTED|PUBLISHED|CITATION)\b", re.IGNORECASE),
    re.compile(r"^\d+\s+[A-Z].+\bUniversity\b.*$", re.IGNORECASE),
]


def is_md_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_heading(line: str) -> bool:
    return line.lstrip().startswith("#")


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    for pattern in PAGE_NOISE_PATTERNS + FIGURE_PATTERNS + METADATA_LINE_PATTERNS:
        if pattern.match(stripped):
            return True
    return False


def clean_text(text: str) -> str:
    text = re.sub(r"<!--\s*PageFooter=.*?-->", "", text)
    text = re.sub(r"<!--\s*PageHeader=.*?-->", "", text)
    text = re.sub(r"<!--\s*PageNumber=.*?-->", "", text)
    text = re.sub(r"(<figure>).*?(</figure>)", r"\1\2", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"閾縗?", "", text)
    text = text.replace("婕?", "")
    lines = text.splitlines()
    out: list[str] = []
    paragraph_buffer: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        joined = " ".join(part.strip() for part in paragraph_buffer if part.strip())
        joined = re.sub(r"\s+", " ", joined).strip()
        if joined:
            out.append(joined)
        paragraph_buffer = []

    for raw in lines:
        line = raw.strip()
        if is_noise_line(line):
            flush_paragraph()
            continue
        if not line:
            flush_paragraph()
            if out and out[-1] != "":
                out.append("")
            continue
        if is_heading(line) or is_md_table_line(line):
            flush_paragraph()
            out.append(line)
            continue
        if re.match(r"^(Abstract|Introduction|References|Acknowledg(?:e)?ments?)$", line, flags=re.IGNORECASE):
            flush_paragraph()
            out.append(f"## {line}")
            continue
        paragraph_buffer.append(line)

    flush_paragraph()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def postprocess_directory(src_dir: Path, dst_dir: Path) -> list[Path]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for md_path in sorted(src_dir.glob("*.md")):
        cleaned = clean_text(md_path.read_text(encoding="utf-8", errors="replace"))
        out_path = dst_dir / md_path.name
        out_path.write_text(cleaned, encoding="utf-8")
        outputs.append(out_path)
    return outputs
