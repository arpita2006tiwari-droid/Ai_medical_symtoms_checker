# Phase 2C Inspection Report

## Vocabulary & Normalization Analysis

Before implementing the NLP symptom extraction service, the `ml/artifacts/symptom_vocabulary.json` and `ml/artifacts/symptom_normalization.json` artifacts were analyzed.

- **Vocabulary**: Contains exactly 131 symptoms in a standardized, spaced format (e.g., `"high fever"`, `"skin rash"`).
- **Normalization**: Maps raw underscored CSV headers (e.g., `" skin_rash"`) to the spaced format.

**Key Finding**:
The normalization map does not introduce any *new* natural language synonyms (like "migraine" -> "headache"). Its sole purpose was to handle CSV column formatting. Therefore, for natural language extraction, the NLP service only needs to target the 131 clean strings present in the `symptom_vocabulary.json`.

## NLP Extraction Design

To achieve strict, deterministic extraction without introducing LLMs or heavy dependencies:
1. **Dynamic Regex Generation**: `nlp_service.py` will read the `symptom_vocabulary.json` upon initialization.
2. **Phrase Sorting**: The 131 vocabulary phrases will be sorted by descending length. This guarantees that multi-word phrases (e.g., "high fever") take matching precedence over single-word overlaps.
3. **Word Boundaries**: The regex pattern will utilize `\b` (word boundaries) combined with `re.IGNORECASE` to extract exact phrase matches, completely avoiding substring false positives (e.g., matching "pain" inside "painting" or accidentally matching "fever" when it isn't explicitly preceded by "high" or "mild").
4. **Duplicate Removal**: A simple `set()` logic will deduplicate matches while preserving discovery order.

This approach ensures zero medical assumption invention and 100% adherence to the existing ML feature bounds.
