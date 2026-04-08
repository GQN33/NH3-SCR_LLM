# PDF Extraction Workflow

## Goal

Convert NH3-SCR PDF papers into:

- raw Markdown
- cleaned final Markdown
- extracted image assets

## Final extraction path

### Core code

- `src/nh3map/pdf/convert_pdf_to_md.py`
- `src/nh3map/pdf/postprocess_md.py`

### Batch runner

- `tool/pdf/process_all_pdfs.py`

## Processing logic

1. Read one or more PDF directories.
2. Deduplicate by filename across input directories.
3. Convert each PDF in parallel.
4. Detect title and main text blocks.
5. Export page images.
6. Convert detected tables to Markdown tables when possible.
7. Fall back to page text extraction when layout parsing is weak.
8. Run Markdown cleanup to remove page noise, some figure captions, and broken paragraphing.

## Recommended command

```powershell
$env:PYTHONPATH='D:/distelling/NH3-SCR_LLM/src'
& D:/design/software/python/python.exe D:/distelling/NH3-SCR_LLM/tool/pdf/process_all_pdfs.py `
  D:/your/pdf_dir_a `
  D:/your/pdf_dir_b `
  --raw-output-dir D:/your/out/raw_md `
  --clean-output-dir D:/your/out/final_md `
  --workers 30
```

## Notes

- This is a PDF-to-Markdown workflow, not a downloader.
- Extracted images are stored next to raw Markdown output under `images/`.
- Final cleaned Markdown is the recommended input for prompt extraction.
