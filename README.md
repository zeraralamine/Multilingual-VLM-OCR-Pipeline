# Multilingual VLM-OCR Pipeline (RTL/LTR)

## The Problem
Traditional OCR systems (like Tesseract) struggle heavily with complex physical documents, specifically:
1. **Mixed Directionality:** Combining Right-to-Left and Left-to-Right text frequently causes grammar scrambling and word skipping.
2. **Dense Layouts:** Double-column formats with page-spanning paragraphs cause OCR engines to read horizontally across the page margin, ruining data flow.
3. **Data Hallucination:** Standard LLMs tasked with formatting messy OCR text into JSON frequently suffer from silent data deletion (dropping "orphaned" sentences to force a perfect JSON schema) or syntax crashes due to unescaped internal quotes.

## The Solution
This repository contains a Tier 3 Vision-Language Model (VLM) pipeline that bypasses traditional OCR limitations. It uses Google's Gemini Flash model combined with a robust Data Engineering pipeline to achieve 100% data integrity via a Human-in-the-Loop (HITL) architecture.

### Key Engineering Features
* **The "Guillotine" Preprocessor (`split.py`):** Automatically slices double-column physical scans into single-column images to eliminate VLM bounding-box collisions and force a strict top-to-bottom reading path.
* **Exception Routing (`extract.py`):** Rather than forcing the AI to output fragile JSON, the prompt categorizes text into 4 strict tags (`[ENTRY]`, `[SUB-ENTRY]`, `[CONTINUATION]`, `[REVIEW]`) using a pipe (`|`) delimiter.
* **Spatial Anchoring:** Instructs the VLM to use physical page features (like horizontal printed margin lines) as absolute boundaries to ignore headers and catchwords.
* **Network Resilience:** Built-in exponential backoff loops to gracefully handle `503 UNAVAILABLE` and `429 RATE LIMIT` API spikes during massive batch processing.

## Broad Use Cases
While originally built for digitizing an 800-page English-Arabic legal dictionary, this architecture is a generalized solution for:
* **Historical Archives:** Digitizing decaying or fuzzy multi-column documents where standard OCR fails.
* **Financial Ledgers & Legal Contracts:** Processing heavily structured, mixed-language documents requiring zero data loss.
* **Academic Papers:** Parsing double-column scientific journals with embedded charts and margin notes.

## Workflow Integration
This pipeline outputs a structured, pipe-delimited text file. The end-user imports this directly into Microsoft Excel, filters out the 95% of perfect `[ENTRY]` rows, and spends minutes (rather than hours) manually stitching the `[CONTINUATION]` exceptions.
