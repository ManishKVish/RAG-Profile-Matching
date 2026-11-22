"""
Job Matching Engine: Semantic + Hybrid Search, Must-Have Filtering & Explainability
Module: job_matcher.py
Produces structured JSON matching the exact assignment specification.
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from resume_rag import VectorStore, load_and_index_resumes

class JobMatcher:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def match(
        self,
        job_description: str,
        must_have_skills: Optional[List[str]] = None,
        min_experience_years: int = 0,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Executes hybrid semantic search + keyword boosting + must-have rule filtering.
        Returns strict output format specified in the project brief.
        """
        must_haves = [s.strip().lower() for s in (must_have_skills or [])]

        # 1. Retrieve candidates via semantic vector search
        raw_retrievals = self.vector_store.search(job_description, top_k=max(60, top_k * 6))

        # 2. Aggregate chunks by candidate
        candidate_agg = {}
        for r in raw_retrievals:
            meta = r["metadata"]
            name = meta.get("name", "Unknown")
            if name not in candidate_agg:
                skills_str = meta.get("skills_str", "")
                skills_list = [s.strip() for s in skills_str.split(",") if s.strip()]
                candidate_agg[name] = {
                    "candidate_name": name,
                    "resume_path": meta.get("filepath", ""),
                    "experience_years": int(meta.get("experience_years", 0)),
                    "skills": skills_list,
                    "semantic_scores": [],
                    "excerpts": []
                }
            candidate_agg[name]["semantic_scores"].append(r["score"])
            if len(candidate_agg[name]["excerpts"]) < 2:
                candidate_agg[name]["excerpts"].append(r["document"][:200].replace("\n", " "))

        scored_candidates = []

        for name, data in candidate_agg.items():
            # Must-have filtering check
            cand_skills_lower = [s.lower() for s in data["skills"]]
            matched_must_haves = [s for s in must_haves if any(s in cs for cs in cand_skills_lower)]
            missing_must_haves = [s for s in must_haves if not any(s in cs for cs in cand_skills_lower)]

            # Check min experience
            exp_gap = max(0, min_experience_years - data["experience_years"])

            # Compute semantic score (0-100)
            avg_semantic = sum(data["semantic_scores"]) / len(data["semantic_scores"])
            semantic_score = min(100.0, avg_semantic * 100.0 * 2.0)

            # Keyword matching score
            matched_skills = [s for s in data["skills"] if s.lower() in job_description.lower()]
            keyword_score = (len(matched_skills) / max(1, len(data["skills"]))) * 100.0

            # Hybrid Score calculation
            raw_score = (0.5 * semantic_score) + (0.5 * keyword_score)

            # Boost for full must-have satisfaction
            if must_haves and not missing_must_haves:
                raw_score += 25.0

            # Penalty for missing must-haves
            if missing_must_haves:
                raw_score -= (len(missing_must_haves) * 20.0)

            # Penalty for experience deficit
            if exp_gap > 0:
                raw_score -= (exp_gap * 10.0)

            final_score = int(max(5, min(98, round(raw_score))))

            # Reasoning synthesis
            reasoning_parts = []
            if matched_skills:
                reasoning_parts.append(f"Strong overlap in core skills: {', '.join(matched_skills[:4])}.")
            if data["experience_years"] >= min_experience_years and min_experience_years > 0:
                reasoning_parts.append(f"Meets experience criteria ({data['experience_years']} yrs vs required {min_experience_years}+ yrs).")
            elif exp_gap > 0:
                reasoning_parts.append(f"Lacks required seniority ({data['experience_years']} yrs vs required {min_experience_years}+ yrs).")
            if missing_must_haves:
                reasoning_parts.append(f"Missing critical must-have requirements: {', '.join(missing_must_haves)}.")

            reasoning = " ".join(reasoning_parts) if reasoning_parts else "General background alignment with position requirements."

            scored_candidates.append({
                "candidate_name": data["candidate_name"],
                "resume_path": data["resume_path"],
                "match_score": final_score,
                "matched_skills": matched_skills,
                "relevant_excerpts": data["excerpts"],
                "reasoning": reasoning
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["match_score"], reverse=True)
        top_matches = scored_candidates[:top_k]

        return {
            "job_description": job_description[:300] + "..." if len(job_description) > 300 else job_description,
            "top_matches": top_matches
        }

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    resumes_dir = base_dir / "data" / "resumes"
    store = load_and_index_resumes(str(resumes_dir))
    matcher = JobMatcher(store)

    sample_jd = (
        "We are looking for a Senior Machine Learning Engineer with 5+ years of experience in "
        "Python, PyTorch, and Docker to build scalable recommendation systems."
    )
    result = matcher.match(
        job_description=sample_jd,
        must_have_skills=["Python", "PyTorch", "Docker"],
        min_experience_years=5,
        top_k=5
    )

    print(json.dumps(result, indent=2))
