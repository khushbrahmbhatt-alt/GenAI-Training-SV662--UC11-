# Multimodal ATS Extraction & Evaluation Engine

An enterprise-grade Generative AI pipeline designed to extract, validate, and evaluate structured data from multimodal resumes (Digital PDFs and Scanned Images). 

This system leverages Azure OpenAI (`gpt-4o-mini`) via direct HTTP requests, enforces strict data contracts using Pydantic schemas, and features a deterministic fuzzy-matching evaluation suite to grade AI extraction against human ground-truth data.

## Project Architecture

```text
GenAI-Training-SV662--UC11-/
│
├── src/
│   ├── extractor.py         # PyMuPDF ingestion (Text & Base64 Image routing)
│   └── engine.py            # Azure OpenAI integration & Pydantic validation
│
├── ui/
│   └── app.py               # Streamlit interactive dashboard
│
├── data/
│   ├── Ground_Truth.xlsx    # Human-curated target data
│   └── Data/                # Nested directory of test resumes (PDFs)
│
├── evaluate_truth.py        # Automated fuzzy-matching evaluation script
├── requirements.txt         # Environment dependencies
└── README.md                # Project documentation