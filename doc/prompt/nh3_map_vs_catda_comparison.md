# NH3_MAP vs CATDA Prompt Comparison

## CATDA reference

The NH3_MAP prompt family was designed against CATDA's staged extraction logic:

- synthesis
- testing
- characterization
- missing-check correction

## NH3_MAP prompt families in this repository

Current production prompts:

- `prompt/map/v003_nh3_map_graph_abstract_prompt_100.md`
- `prompt/map/v005_nh3_map_synthesis_prompt.md`
- `prompt/map/v005_nh3_map_testing_prompt.md`
- `prompt/map/v005_nh3_map_characterization_prompt.md`
- `prompt/map/v005_nh3_map_missing_check_prompt.md`

Archived baselines:

- `prompt/archive/map/v002_nh3_map_graph_abstract_prompt_50.md`
- `prompt/archive/map/v004_nh3_map_synthesis_prompt.md`
- `prompt/archive/map/v004_nh3_map_testing_prompt.md`
- `prompt/archive/map/v004_nh3_map_characterization_prompt.md`
- `prompt/archive/map/v004_nh3_map_missing_check_prompt.md`

## Structural comparison

CATDA:

- strong staged separation
- explicit recovery and correction logic
- chemistry-general schema
- tuned for full-text extraction

NH3_MAP:

- keeps staged extraction
- adds one compact abstract-oriented graph prompt
- narrows the schema around NH3-SCR catalysts and catalyst states
- handles noisier PDF-derived Markdown

## Content focus comparison

CATDA is stronger at:

- general catalyst graph extraction
- broad chemistry coverage
- full synthesis reconstruction in a chemistry-agnostic setting

NH3_MAP is stronger at:

- low-temperature NH3-SCR domain fit
- sulfur, water, alkali, phosphorus, zinc, and hydrothermal-aging studies
- explicit `poisoned_catalyst` modeling
- abstract-level screening before full-text extraction

## Practical recommendation

- Use NH3_MAP `v003` for broad abstract screening.
- Use NH3_MAP `v005` staged prompts for selected full-text production extraction.
- Keep archived `v002` and `v004` only for regression comparison.
