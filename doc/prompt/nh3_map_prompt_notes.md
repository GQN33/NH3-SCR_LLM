# NH3_MAP Prompt Design Notes

## Sources used

- graph schema seed from the NH3_MAP graph framework document used during design
- CATDA prompt structure from:
  - `extract_prompts.py`
  - `features_to_extract.txt`
- random abstract samples from cleaned Markdown:
  - `prompt/samples/abstract_sample_50.json`
  - `prompt/samples/abstract_sample_100.json`

## Graph schema adopted

Nodes:

- `paper`
- `chemical`
- `catalyst`
- `poisoned_catalyst`
- `preparation`
- `testing`
- `characterization`

Edges:

- `preparation_input`
- `preparation_output`
- `test_input`
- `test_output`
- `characterization_input`
- `characterization_output`
- `appear_in`

## What was borrowed from CATDA

- stage-oriented prompt structure instead of one generic extractor
- explicit sections for objective, schema, rules, and output format
- strict JSON-only output
- strong evidence anchoring
- aggressive negative rules to suppress hallucination
- conservative normalization rules

## What changed for NH3_MAP

- narrower focus on low-temperature NH3-SCR catalyst literature
- better tolerance to noisy PDF-derived Markdown
- dedicated `poisoned_catalyst` node
- stronger NH3-SCR testing and deactivation modeling

## Recurrent patterns found in sampled abstracts

- catalyst families:
  - Mn-based mixed oxides
  - Ce-Mn, Fe-Mn, Cu-SSZ-13, Fe-zeolites, V-W/Ti systems
  - carbon-supported catalysts
  - slag-derived and waste-derived catalysts
  - composite and dual-functional systems
- preparation cues:
  - impregnation
  - ion exchange
  - hydrothermal synthesis
  - sol-gel
  - co-precipitation
  - ball milling
  - calcination
- testing conditions:
  - temperature window
  - GHSV or WHSV
  - feed composition for NO, NH3, O2, H2O, SO2
  - hydrothermal aging
  - poisoning tests
- result metrics:
  - NOx conversion
  - N2 selectivity
  - active temperature window
  - SO2 and H2O tolerance
  - hydrothermal stability
  - low-temperature activity
- characterization mentions:
  - BET
  - XRD
  - XPS
  - H2-TPR
  - NH3-TPD
  - DRIFTS and in situ DRIFTS
  - SEM and TEM

## Known limitations

- abstract-only extraction cannot recover full preparation detail reliably
- noisy Markdown still requires strong metadata suppression
- some schema edges are retained for compatibility with the original graph sketch
