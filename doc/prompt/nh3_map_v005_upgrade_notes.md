# NH3_MAP v005 Upgrade Notes

Built from the 50-paper full-text calibration set.

Main upgrades over `v004`:

- stronger `preparation` granularity for multi-step full-text synthesis
- explicit `poisoned_catalyst` state generation and parent-child tracking
- broader NH3-SCR testing scenario coverage:
  - standard SCR
  - fast SCR
  - NO2-SCR
  - sulfur and water tolerance
  - hydrothermal and chemical aging
  - regeneration
  - AdSCR and integrated systems
- stronger `characterization` handling for state-specific evidence
- stronger `missing_check` rules for fresh vs aged vs poisoned separation

Recommended use:

- `v003`: abstract-level fast screening
- `v005`: production extraction on selected full-text papers
