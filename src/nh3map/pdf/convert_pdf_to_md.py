from __future__ import annotations

import html
import random
import re
from pathlib import Path

import fitz

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


MIN_PAGE_STRUCTURED_CHARS = 240
MIN_DOC_OUTPUT_CHARS = 1200
MIN_IMAGE_EDGE = 120


def sanitize_stem(name: str) -> str:
    cleaned = html.unescape(name)
    cleaned = re.sub(r"[<>:\"/\\|?*]+", "_", cleaned).strip()
    return cleaned or "document"


def normalize_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"-\s+\n\s*", "", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_noise_text(text: str) -> bool:
    low = text.lower().strip()
    if not low:
        return True
    if any(token in low for token in ("doi:", "issn", "copyright", "open access")):
        return True
    if low in {"article", "review", "communication", "full paper"}:
        return True
    if re.fullmatch(r"\d+", low):
        return True
    if re.match(r"^(figure|fig\.?|scheme)\s*\d+", low, flags=re.IGNORECASE):
        return True
    if re.match(r"^(figure|fig\.?|scheme)\s+[a-z]\b", low, flags=re.IGNORECASE):
        return True
    if "graphical abstract" in low:
        return True
    return False


def normalize_text_preserve_paragraphs(text: str) -> list[str]:
    text = html.unescape(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r", "")
    chunks = re.split(r"\n\s*\n+", text)
    paragraphs: list[str] = []
    for chunk in chunks:
        normalized = normalize_text(chunk)
        if normalized and not is_noise_text(normalized):
            paragraphs.append(normalized)
    return paragraphs


def is_heading(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) > 140:
        return False
    if re.match(r"^\d+(\.\d+)*\s+[A-Z]", stripped):
        return True
    if re.match(
        r"^(abstract|introduction|experimental|methods?|results? and discussion|results|discussion|conclusions?|references|acknowledg\w+)\b",
        stripped,
        flags=re.IGNORECASE,
    ):
        return True
    words = stripped.split()
    return 1 <= len(words) <= 12 and stripped.upper() == stripped and re.search(r"[A-Z]", stripped) is not None


def block_text(block: dict) -> tuple[str, float]:
    parts = []
    sizes = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            text = span.get("text", "")
            if text:
                parts.append(text)
                sizes.append(float(span.get("size", 0.0)))
    return normalize_text(" ".join(parts)), (max(sizes) if sizes else 0.0)


def bbox_overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0)


def rows_to_md_table(rows: list[list[str]]) -> str:
    width = max(len(row) for row in rows if row) if rows else 0
    cleaned_rows = []
    for row in rows:
        cells = [normalize_text(str(cell)) for cell in row]
        cells += [""] * (width - len(cells))
        cleaned_rows.append(cells)
    cleaned_rows = [row for row in cleaned_rows if any(cell for cell in row)]
    if not cleaned_rows or width < 2:
        return ""

    header = cleaned_rows[0]
    body = cleaned_rows[1:] if len(cleaned_rows) > 1 else []
    sep = ["---"] * width

    def render(row: list[str]) -> str:
        safe = [cell.replace("|", "\\|") for cell in row]
        return "| " + " | ".join(safe) + " |"

    return "\n".join([render(header), render(sep)] + [render(row) for row in body])


def extract_page_items(page: fitz.Page) -> list[tuple[float, str, str]]:
    items: list[tuple[float, str, str]] = []
    table_bboxes: list[tuple[float, float, float, float]] = []
    try:
        tables = page.find_tables()
        for table in tables.tables:
            md_table = rows_to_md_table(table.extract())
            if md_table:
                table_bboxes.append(tuple(table.bbox))
                items.append((float(table.bbox[1]), "table", md_table))
    except Exception:
        pass

    blocks = page.get_text("dict").get("blocks", [])
    page_height = float(page.rect.height)
    for block in blocks:
        if block.get("type") != 0:
            continue
        bbox = tuple(block.get("bbox", (0, 0, 0, 0)))
        y0, y1 = float(bbox[1]), float(bbox[3])
        if y0 < 35 or y1 > page_height - 25:
            continue
        if any(bbox_overlaps(bbox, tb) for tb in table_bboxes):
            continue
        text, max_size = block_text(block)
        if not text or is_noise_text(text):
            continue
        kind = "heading" if is_heading(text) or max_size >= 15 else "para"
        items.append((y0, kind, text))

    items.sort(key=lambda item: item[0])
    return items


def fallback_page_paragraphs(page: fitz.Page) -> list[str]:
    return normalize_text_preserve_paragraphs(page.get_text("text"))


def fallback_doc_paragraphs_pypdf(pdf_path: Path) -> list[str]:
    if PdfReader is None:
        return []
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return []
    paragraphs: list[str] = []
    for page in reader.pages:
        paragraphs.extend(normalize_text_preserve_paragraphs(page.extract_text() or ""))
    return paragraphs


def detect_title(doc: fitz.Document, pdf_path: Path) -> str:
    if not doc:
        return pdf_path.stem
    first_page = doc[0]
    candidates: list[tuple[float, float, str]] = []
    for block in first_page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        bbox = tuple(block.get("bbox", (0, 0, 0, 0)))
        y0 = float(bbox[1])
        if y0 > first_page.rect.height * 0.45:
            continue
        text, max_size = block_text(block)
        if not text or is_noise_text(text):
            continue
        if len(text) > 220:
            continue
        if re.search(r"\b(?:doi|issn|copyright|received|accepted|published)\b", text, flags=re.IGNORECASE):
            continue
        if re.search(r"\b\d{4}\b", text) and re.search(r":\s*\d", text):
            continue
        if re.search(r"\b(abstract|introduction|keywords)\b", text, flags=re.IGNORECASE):
            continue
        candidates.append((max_size, -y0, text))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][2]
    return pdf_path.stem


def export_page_images(page: fitz.Page, image_dir: Path) -> int:
    image_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    seen_xrefs: set[int] = set()
    for index, image_info in enumerate(page.get_images(full=True), start=1):
        xref = int(image_info[0])
        if xref in seen_xrefs:
            continue
        seen_xrefs.add(xref)
        try:
            image_dict = page.parent.extract_image(xref)
        except Exception:
            continue
        width = int(image_dict.get("width", 0))
        height = int(image_dict.get("height", 0))
        if width < MIN_IMAGE_EDGE or height < MIN_IMAGE_EDGE:
            continue
        ext = (image_dict.get("ext") or "png").lower()
        if ext == "jpeg":
            ext = "jpg"
        out_path = image_dir / f"page{page.number + 1:02d}_img{index:02d}.{ext}"
        out_path.write_bytes(image_dict["image"])
        saved += 1
    return saved


def convert_pdf(pdf_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{sanitize_stem(pdf_path.stem)}.md"
    image_dir = output_dir / "images" / sanitize_stem(pdf_path.stem)
    paragraphs: list[str] = []
    exported_images = 0
    with fitz.open(pdf_path) as doc:
        title = detect_title(doc, pdf_path)
        paragraphs.extend([f"# {title}", "", f"Source PDF: `{pdf_path.name}`", ""])
        for page in doc:
            exported_images += export_page_images(page, image_dir)
            page_items = extract_page_items(page)
            structured_chars = sum(len(text) for _, kind, text in page_items if kind != "table")
            if not page_items or structured_chars < MIN_PAGE_STRUCTURED_CHARS:
                page_blocks = fallback_page_paragraphs(page)
                if page_blocks:
                    paragraphs.extend([f"<!-- PageBreak {page.number + 1} -->", ""])
                    for para in page_blocks:
                        if para == title or para.startswith(title + " "):
                            continue
                        paragraphs.extend([para, ""])
                    continue
            for _, kind, text in page_items:
                if kind == "table":
                    paragraphs.extend([text, ""])
                    continue
                if text == title or text.startswith(title + " "):
                    continue
                paragraphs.extend([f"## {text}" if kind == "heading" else text, ""])

    body = re.sub(r"\n{3,}", "\n\n", "\n".join(paragraphs).strip() + "\n")
    if len(body) < MIN_DOC_OUTPUT_CHARS:
        fallback_paragraphs = fallback_doc_paragraphs_pypdf(pdf_path)
        if fallback_paragraphs:
            lines = [f"# {title}", "", f"Source PDF: `{pdf_path.name}`", ""]
            for para in fallback_paragraphs:
                if para == title or para.startswith(title + " "):
                    continue
                lines.extend([para, ""])
            body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).strip() + "\n")

    if exported_images:
        body += f"\n<!-- Extracted images: images/{sanitize_stem(pdf_path.stem)}/ ({exported_images}) -->\n"
    elif image_dir.exists():
        try:
            image_dir.rmdir()
        except OSError:
            pass

    output_path.write_text(body, encoding="utf-8")
    return output_path


def convert_from_manifest(pdf_dir: Path, output_dir: Path, manifest: Path) -> list[Path]:
    selected = [pdf_dir / line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [convert_pdf(pdf, output_dir) for pdf in selected if pdf.exists()]


def sample_and_convert(pdf_dir: Path, output_dir: Path, manifest: Path, sample_size: int) -> list[Path]:
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if len(pdfs) < sample_size:
        raise RuntimeError(f"Need at least {sample_size} PDFs, found {len(pdfs)}")
    selected = random.sample(pdfs, sample_size)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("\n".join(pdf.name for pdf in selected) + "\n", encoding="utf-8")
    return [convert_pdf(pdf, output_dir) for pdf in selected]
