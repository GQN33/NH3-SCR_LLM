# NH3_MAP Full-Text Calibration Set 50

## Purpose

This set was selected to harden the staged NH3_MAP prompts beyond abstract-only extraction.

Main calibration targets:

- multi-step `preparation`
- explicit `poisoned_catalyst` handling
- richer `testing.condition` capture
- state-aware `characterization` evidence

## Selection logic

- not random
- balanced across catalyst families and study styles
- biased toward papers that add prompt-design value

## Coverage summary

- `review`: 5
- `mn_based`: 13
- `ce_based`: 7
- `fe_based`: 8
- `cu_based`: 12
- `v_based`: 6
- `zeolite`: 16
- `poisoning`: 14
- `aging`: 5
- `mechanism`: 18
- `support_waste`: 3
- `composite_dual`: 4

## Repository asset

The calibration filenames are listed in:

- `prompt/samples/fulltext_calibration_50.txt`

The actual Markdown or PDF files are intentionally not tracked in this repository.

## Why this set matters

Compared with abstract-only prompt design, these full-text papers expose:

- synthesis order and processing detail
- catalyst-state transitions such as `fresh`, `aged`, `poisoned`, and `regenerated`
- richer NH3-SCR testing conditions
- characterization evidence tied to specific catalyst states
