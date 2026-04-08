# Project Overview

## Goal

Build a maintainable pipeline that turns NH3 low-temperature catalyst literature into:

- searchable structured knowledge
- reproducible prompt-driven extraction workflows
- multimodal feature sets from text, tables, and figures
- model-ready catalyst datasets
- inverse-design suggestions from target performance constraints

## Planned Capability Layers

### 1. Literature Layer

- WoS query prompts
- screening prompts
- deduplication and DOI management
- raw metadata preservation

### 2. Document Layer

- PDF to Markdown conversion
- page image extraction
- figure and caption pairing
- table normalization

### 3. Extraction Layer

- MAP-generated or MAP-managed prompts
- synthesis / characterization / testing extraction
- evidence tracking
- versioned prompt templates

### 4. Multimodal Layer

- figure classification
- chart reading
- microscopy or schematic interpretation
- text-image alignment

### 5. Inverse Design Layer

- define target inputs such as activity, selectivity, SO2 tolerance, H2O tolerance, temperature window
- retrieve similar catalysts and synthesis patterns
- generate candidate composition and preparation suggestions
- record rationale and evidence provenance

## Near-Term Build Order

1. stabilize literature and document preprocessing
2. formalize prompt directories and schemas
3. add structured extraction package code
4. add multimodal interfaces
5. add inverse-design experiment loop
