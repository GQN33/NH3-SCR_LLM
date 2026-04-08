# NH3_MAP Prompt Summary

## Current production prompt set

### Abstract screening

- `prompt/map/v003_nh3_map_graph_abstract_prompt_100.md`
  - purpose: fast abstract-level graph extraction
  - best use: large-scale first-pass screening
  - strength: broad NH3-SCR coverage with one-shot output
  - tradeoff: less controllable than staged full-text extraction

### Full-text staged extraction

- `prompt/map/v005_nh3_map_synthesis_prompt.md`
  - extracts catalyst, poisoned-catalyst, preparation, and synthesis-linked chemicals
- `prompt/map/v005_nh3_map_testing_prompt.md`
  - extracts NH3-SCR testing scenarios, conditions, and performance results
- `prompt/map/v005_nh3_map_characterization_prompt.md`
  - extracts characterization methods, findings, and state-specific evidence
- `prompt/map/v005_nh3_map_missing_check_prompt.md`
  - performs a final correction pass over the merged graph

## Archived baselines

- `prompt/archive/map/v002_nh3_map_graph_abstract_prompt_50.md`
  - earlier compact prompt
- `prompt/archive/map/v004_*`
  - first staged NH3_MAP family
  - useful as a regression baseline

## Design logic

This prompt family follows CATDA's staged extraction idea but narrows the schema around NH3-SCR-specific catalyst states and testing conditions.

Main NH3_MAP additions over generic catalyst prompts:

- explicit `poisoned_catalyst`
- stronger sulfur, water, alkali, phosphorus, zinc, and hydrothermal-aging handling
- stronger separation of `fresh`, `aged`, `poisoned`, and `regenerated` catalyst states
- extraction logic aligned with later performance-to-recipe workflows

## Recommended usage

1. Screen broad literature with `v003`.
2. Run staged `v005` prompts on selected full-text papers.
3. Use the missing-check stage before graph persistence or downstream analysis.
