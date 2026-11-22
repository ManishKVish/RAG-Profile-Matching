"""
RAG System Setup: Document Chunking, Embedding & Vector Store Indexing
Module: resume_rag.py
Loads resumes, extracts metadata, chunks text while preserving sections,
and indexes vectors into ChromaDB / Persistent Vector Store.
"""
import os
import re
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

class DocumentChunker:
    """Intelligently chunks resumes while preserving semantic sections."""
    SECTION_HEADERS = [
        "PROFESSIONAL SUMMARY", "SUMMARY", "WORK EXPERIENCE", "EXPERIENCE",
        "EDUCATION", "SKILLS", "TECHNICAL SKILLS", "PROJECTS", "CERTIFICATIONS"
    ]

    @staticmethod
    def chunk_document(text: str, candidate_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        chunks = []
        lines = text.splitlines()
        current_section = "GENERAL"
        current_lines = []

        for line in lines:
            stripped = line.strip()
            # Detect section header with exact boundary (e.g. "WORK EXPERIENCE:" or "EDUCATION")
            matched_header = None
            header_pattern = r'^(?:' + '|'.join(DocumentChunker.SECTION_HEADERS) + r')[:\s]*$'
            if re.match(header_pattern, stripped, re.IGNORECASE):
                # Normalize header
                for h in DocumentChunker.SECTION_HEADERS:
                    if stripped.upper().startswith(h):
                        matched_header = h
                        break

            if matched_header:
                if current_lines:
                    chunk_text = "\n".join(current_lines).strip()
                    if chunk_text:
                        chunks.append({
                            "section": current_section,
                            "content": chunk_text,
                            "metadata": {**candidate_metadata, "section": current_section}
                        })
                    current_lines = []
                current_section = matched_header
            else:
                if stripped:
                    current_lines.append(stripped)

        if current_lines:
            chunk_text = "\n".join(current_lines).strip()
            if chunk_text:
                chunks.append({
                    "section": current_section,
                    "content": chunk_text,
                    "metadata": {**candidate_metadata, "section": current_section}
                })

        return chunks

class MetadataExtractor:
    """Extracts structured metadata: Name, Skills, Experience Years, Education."""
    @staticmethod
    def extract(text: str) -> Dict[str, Any]:
        metadata = {
            "name": "Unknown Candidate",
            "title": "",
            "experience_years": 0,
            "skills": [],
            "education": ""
        }

        # Name
        m_name = re.search(r'NAME:\s*([^\n\r]+)', text, re.IGNORECASE)
        if m_name:
            metadata["name"] = m_name.group(1).strip()

        # Title
        m_title = re.search(r'TITLE:\s*([^\n\r]+)', text, re.IGNORECASE)
        if m_title:
            metadata["title"] = m_title.group(1).strip()

        # Experience
        m_exp = re.search(r'EXPERIENCE:\s*(\d+)', text, re.IGNORECASE)
        if m_exp:
            metadata["experience_years"] = int(m_exp.group(1))

        # Education
        m_edu = re.search(r'EDUCATION:\s*([^\n\r]+)', text, re.IGNORECASE)
        if m_edu:
            metadata["education"] = m_edu.group(1).strip()

        # Skills
        m_skills = re.search(r'SKILLS:\s*([^\n\r]+)', text, re.IGNORECASE)
        if m_skills:
            raw_skills = m_skills.group(1).split(",")
            metadata["skills"] = [s.strip() for s in raw_skills if s.strip()]

        return metadata

class VectorStore:
    """Manages document embeddings, indexing, and similarity search."""
    def __init__(self, collection_name: str = "resumes_collection", persist_dir: Optional[str] = None):
        self.collection_name = collection_name
        self.persist_dir = persist_dir or str(Path(__file__).parent / "data" / "chroma_db")
        self.client = None
        self.collection = None
        self.fallback_docs = [] # In-memory fallback if native chromadb bindings vary

        if chromadb:
            try:
                self.client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.client.get_or_create_collection(name=collection_name)
            except Exception as e:
                print(f"ChromaDB initialization notice (using memory fallback): {e}")

    def embed_text(self, text: str) -> List[float]:
        """Generates deterministic TF-IDF / term-frequency vector embedding."""
        words = re.findall(r'\b[a-zA-Z0-9_\+#\.]+\b', text.lower())
        vector = [0.0] * 128
        for word in words:
            # Deterministic hash to 128 dimensions
            idx = abs(hash(word)) % 128
            vector[idx] += 1.0

        # Normalize to unit length (L2 norm)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

    def index_resume(self, resume_id: str, filepath: str, text: str, metadata: Dict[str, Any]):
        chunks = DocumentChunker.chunk_document(text, metadata)
        embeddings = [self.embed_text(c["content"]) for c in chunks]
        ids = [f"{resume_id}_chunk_{i}" for i in range(len(chunks))]
        documents = [c["content"] for c in chunks]
        metadatas = []
        for c in chunks:
            clean_meta = dict(c["metadata"])
            clean_meta["skills_str"] = ", ".join(clean_meta.get("skills", []))
            clean_meta.pop("skills", None)
            clean_meta["filepath"] = filepath
            metadatas.append(clean_meta)

        if self.collection:
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            except Exception:
                pass

        # Also store in fallback memory index
        for cid, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
            self.fallback_docs.append({
                "id": cid,
                "document": doc,
                "embedding": emb,
                "metadata": meta
            })

    def search(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        query_emb = self.embed_text(query_text)
        scored_results = []

        if self.collection and self.collection.count() > 0:
            try:
                results = self.collection.query(
                    query_embeddings=[query_emb],
                    n_results=min(top_k * 2, self.collection.count())
                )
                if results and "documents" in results and results["documents"]:
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                        # Compute similarity
                        doc_emb = self.embed_text(doc)
                        dot_prod = sum(a * b for a, b in zip(query_emb, doc_emb))
                        scored_results.append({
                            "document": doc,
                            "metadata": meta,
                            "score": max(0.0, min(1.0, dot_prod))
                        })
                    scored_results.sort(key=lambda x: x["score"], reverse=True)
                    return scored_results[:top_k]
            except Exception:
                pass

        # Fallback in-memory search
        for item in self.fallback_docs:
            doc_emb = item["embedding"]
            dot_prod = sum(a * b for a, b in zip(query_emb, doc_emb))
            scored_results.append({
                "document": item["document"],
                "metadata": item["metadata"],
                "score": max(0.0, min(1.0, dot_prod))
            })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

def load_and_index_resumes(resumes_dir: str, vector_store: Optional[VectorStore] = None) -> VectorStore:
    store = vector_store or VectorStore()
    dir_path = Path(resumes_dir)
    count = 0
    for file_path in dir_path.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        meta = MetadataExtractor.extract(text)
        resume_id = file_path.stem
        store.index_resume(resume_id, str(file_path), text, meta)
        count += 1
    print(f"Indexed {count} resumes into VectorStore successfully.")
    return store

if __name__ == "__main__":
    resumes_dir = Path(__file__).parent / "data" / "resumes"
    store = load_and_index_resumes(str(resumes_dir))
    results = store.search("Python machine learning PyTorch recommendation system", top_k=3)
    print("\nTop 3 Sample Retrieval Results:")
    for r in results:
        print(f"  • {r['metadata'].get('name')} (Score: {r['score']:.3f}) | Section: {r['metadata'].get('section')}")
