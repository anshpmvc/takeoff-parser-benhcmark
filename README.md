# Takeoff Parser Benchmark

A computer vision pipeline that extracts construction material takeoffs from architectural blueprint PDFs.

## What this does
Converts blueprint PDF pages into high-resolution images, runs object detection models against them, and outputs structured JSON takeoff data (material, quantity, unit, location).

## Current status
Work in progress — core pipeline is functional, accuracy is early-stage.

### What works
- PDF → 600 DPI image conversion (PyMuPDF)
- Roboflow object detection on blueprint pages
- Streamlit UI — upload PDF, select page, view detections
- Standardized JSON output schema across all parsers
- Swappable model architecture — adding new parsers requires one new file

### What doesn't work yet
- VLM semantic extraction (Ollama/Llama3.2-vision times out on M2 locally — needs API key for Claude or Gemini)
- Bounding boxes not yet rendered on blueprint image in UI
- Accuracy is low on elevation drawings — Roboflow model trained on floor plans, not elevations

## Architecture
```
Blueprint PDF
     ↓
pdf_to_images.py       — converts pages to 600 DPI PNG
     ↓
roboflow_parser.py     — object detection via Roboflow API
ollama_parser.py       — local VLM extraction (blocked, see above)
     ↓
orchestrator.py        — merges parser outputs (not yet implemented)
     ↓
app.py                 — Streamlit UI
```

## Stack
- Python 3.12
- PyMuPDF — PDF to image conversion
- Roboflow inference SDK — pretrained construction models
- Ollama + Llama3.2-vision — local VLM (pending)
- Streamlit — UI

## How to run
```bash
git clone git@github.com:anshpmvc/takeoff-parser-benhcmark.git
cd takeoff-parser-benhcmark
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "ROBOFLOW_API_KEY=your_key" > .env
streamlit run app.py
```

## Next steps
- Add Gemini/Claude Vision API parser for semantic extraction
- Render bounding boxes on blueprint image in UI
- Find Roboflow models trained on elevation drawings specifically
- Build eval layer — ground truth annotation + precision/recall scoring
- Fine-tune on KIQ-specific blueprint types

## Sample data
Florence Apartments Exterior Finishes Takeoff — 5 page PDF including quantity takeoff sheets (pages 1-2) and color-coded elevation drawings (pages 3-5).
```

Save it. Then commit:
```
git add README.md && git commit -m "update README with honest status, architecture and next steps" && git push origin main