# Tool Layout

## PDF tools

- `pdf/process_all_pdfs.py`
  - main batch entrypoint
  - supports multiple PDF input directories
  - runs parallel PDF-to-Markdown conversion and final cleanup
- `pdf/convert_sample_pdfs.py`
  - small-sample conversion helper
- `pdf/postprocess_md.py`
  - cleanup-only entrypoint

## Prompt tools

- `prompts/prompt_eval.py`
  - random-sample prompt comparison runner
  - supports OpenAI Responses API and OpenAI-compatible chat-completions endpoints

Keep reusable logic in `src/nh3map/`. Keep `tool/` as thin wrappers only.
