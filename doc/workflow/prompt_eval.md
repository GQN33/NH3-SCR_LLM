# Prompt Eval Workflow

## Purpose

Compare NH3_MAP prompt variants on a random markdown sample.

Current compared profiles:

- `compact_100`
- `staged_v005`
- `archive_compact_50`
- `archive_staged_v004`

## Inputs

- cleaned markdown directory, for example:
  - `D:\your\final_md`
- API key in `OPENAI_API_KEY`
- supports OpenAI Responses API and OpenAI-compatible `chat/completions` endpoints

## Example

```powershell
$env:PYTHONPATH='D:/distelling/NH3-SCR_LLM/src'
$env:OPENAI_API_KEY='YOUR_KEY'
& D:/design/software/python/python.exe D:/distelling/NH3-SCR_LLM/tool/prompts/prompt_eval.py `
  --md-dir D:/your/final_md `
  --out-dir D:/your/eval/run_001 `
  --model deepseek-chat `
  --api-url https://api.deepseek.com/chat/completions `
  --sample-size 24 `
  --seed 20260408 `
  --include-missing-check
```

## Outputs

- `selected_files.json`
- one folder per profile
- one folder per paper inside each profile
- `graph.json`
- `metrics.json`
- raw model outputs per stage
- top-level `eval_summary.json`

## Main summary metrics

- success rate
- average nodes
- average edges
- average latency
- catalyst coverage rate
- testing coverage rate
- characterization coverage rate
