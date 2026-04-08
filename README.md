# NH3-SCR_LLM

This repository contains the current NH3-SCR literature extraction workflow, prompt set, and evaluation utilities for low-temperature NH3-SCR catalyst research.

## What Is Included

- `prompt/`
  - production prompt set for NH3_MAP extraction
  - WoS retrieval, multimodal, and inverse-design prompt stubs
  - archived prompt versions and calibration samples
- `src/nh3map/`
  - reusable Python code for PDF-to-Markdown conversion, Markdown cleanup, and prompt evaluation
- `tool/`
  - runnable entry scripts for batch PDF extraction and prompt evaluation
- `doc/`
  - prompt design notes, CATDA comparison, calibration-set notes, and workflow docs

## Current Recommended Prompt Set

- Abstract screening:
  - `prompt/map/v003_nh3_map_graph_abstract_prompt_100.md`
- Full-text production extraction:
  - `prompt/map/v005_nh3_map_synthesis_prompt.md`
  - `prompt/map/v005_nh3_map_testing_prompt.md`
  - `prompt/map/v005_nh3_map_characterization_prompt.md`
  - `prompt/map/v005_nh3_map_missing_check_prompt.md`

Older prompt versions are retained under `prompt/archive/map/` for comparison only.

## Current Recommended PDF Tooling

- Core library:
  - `src/nh3map/pdf/convert_pdf_to_md.py`
  - `src/nh3map/pdf/postprocess_md.py`
- Batch entrypoint:
  - `tool/pdf/process_all_pdfs.py`

This is the current final extraction path:

1. Convert PDF to Markdown and export images
2. Clean Markdown into final reading and extraction form
3. Run prompt extraction and evaluation on cleaned Markdown

## Example Commands

Set Python import path first:

```powershell
$env:PYTHONPATH='D:/distelling/NH3-SCR_LLM/src'
```

Batch PDF extraction:

```powershell
& D:/design/software/python/python.exe D:/distelling/NH3-SCR_LLM/tool/pdf/process_all_pdfs.py `
  D:/your/pdf_dir_a `
  D:/your/pdf_dir_b `
  --raw-output-dir D:/your/out/raw_md `
  --clean-output-dir D:/your/out/final_md `
  --workers 30
```

Prompt evaluation:

```powershell
$env:OPENAI_API_KEY='YOUR_KEY'
& D:/design/software/python/python.exe D:/distelling/NH3-SCR_LLM/tool/prompts/prompt_eval.py `
  --md-dir D:/your/out/final_md `
  --out-dir D:/your/eval/run_001 `
  --model deepseek-chat `
  --api-url https://api.deepseek.com/chat/completions `
  --sample-size 24 `
  --include-missing-check
```

## Document Guide

- Prompt summary:
  - `doc/prompt/prompt_summary.md`
- CATDA comparison:
  - `doc/prompt/nh3_map_vs_catda_comparison.md`
- v005 upgrade notes:
  - `doc/prompt/nh3_map_v005_upgrade_notes.md`
- Prompt evaluation workflow:
  - `doc/workflow/prompt_eval.md`
- PDF and literature workflow notes:
  - `doc/workflow/literature_pipeline.md`
  - `doc/workflow/multimodal_pipeline.md`
