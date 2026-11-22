# RAG-Based Profile Matching

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Vector DB](https://img.shields.io/badge/ChromaDB-Vector%20Store-purple.svg)]()
[![Retrieval](https://img.shields.io/badge/Hybrid%20Search-Semantic%20%2B%20Keyword-success.svg)]()
[![Airtribe Assignment](https://img.shields.io/badge/Airtribe-Backend%20AI%20Track-orange.svg)]()

This repository contains the complete implementation for **Milestone 2 (RAG Based Profile matching)** of the Airtribe Backend AI track.

---

## 🎯 Architecture & Highlights

1. **Document Processing Pipeline (`resume_rag.py`)**:
   - Parses resumes using file system extraction.
   - **Intelligent Section-Aware Chunking**: Preserves discrete boundaries (`SUMMARY`, `WORK EXPERIENCE`, `EDUCATION`, `SKILLS`, `CERTIFICATIONS`).
   - Dense vector embeddings indexed in **ChromaDB**.
   - Structured metadata extraction (`candidate_name`, `skills`, `experience_years`, `education`).
2. **Job Matching Engine (`job_matcher.py`)**:
   - Semantic retrieval mapping Job Description text to candidate vectors ($K=10$).
   - **Hybrid Search**: Fuses semantic cosine similarity ($0.5$), exact keyword coverage ($0.5$), and must-have skill filtering penalties.
   - Output adheres strictly to the assignment's specified JSON format.
3. **Dataset**:
   - **30+ Diverse Resumes**: Spanning Machine Learning, Backend (Python, Go, Java), DevOps (Kubernetes, AWS, Terraform), Full Stack (React, Node), and Data Engineering.
   - **5 Production Job Descriptions**: Covering distinct engineering specialties.
4. **Experimentation & Analysis (`experiments.ipynb`)**:
   - Analysis of chunking strategies, retrieval latency benchmarks ($<15\text{ ms}$ query latency), and hybrid search accuracy.

---

## 📁 Repository Structure

```
├── resume_rag.py             # Part A: Document chunking, metadata extraction & vector indexing
├── job_matcher.py            # Part B: Semantic + hybrid search, scoring, and explainability
├── create_dataset.py         # Generates 30+ resumes and 5 job descriptions
├── experiments.ipynb         # Jupyter notebook with benchmarking and analysis
├── data/
│   ├── resumes/              # 30+ sample candidate resumes
│   └── job_descriptions/    # 5 realistic job descriptions (JSON)
├── tests/
│   └── test_rag.py           # Automated test suite
├── requirements.txt
└── README.md
```

---

## 📋 Exact Output JSON Specification

```json
{
  "job_description": "We are looking for a Senior Machine Learning Engineer with 5+ years of experience in Python, PyTorch, and Docker...",
  "top_matches": [
    {
      "candidate_name": "John Doe",
      "resume_path": "data/resumes/resume_john_doe.txt",
      "match_score": 86,
      "matched_skills": ["Python", "Machine Learning", "PyTorch", "Docker"],
      "relevant_excerpts": [
        "Senior Role (2021 - Present): - Core contributions and architectural execution across Python, Machine Learning, PyTorch."
      ],
      "reasoning": "Strong overlap in core skills: Python, Machine Learning, PyTorch, Docker. Meets experience criteria (6 yrs vs required 5+ yrs)."
    }
  ]
}
```

---

## 🏃 Setup & Verification

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated tests
python -m unittest discover tests

# 3. Execute matching engine
python job_matcher.py
```
