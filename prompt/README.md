# Prompt Layout

## Production prompts

- `map/`
  - current NH3_MAP prompts for abstract screening and staged full-text extraction
- `wos/`
  - literature retrieval prompts
- `multimodal/`
  - figure and multimodal analysis prompts
- `inverse_design/`
  - target-performance-to-catalyst prompts

## Supporting assets

- `samples/`
  - abstract samples and full-text calibration list used during prompt design

## Archived prompts

- `archive/map/`
  - earlier NH3_MAP prompt versions kept for comparison and regression checking

## Current recommendation

- Use `map/v003_nh3_map_graph_abstract_prompt_100.md` for abstract-level screening.
- Use the `map/v005_*` staged prompts for selected full-text extraction.
- Treat `archive/` files as baselines, not as the default production set.
