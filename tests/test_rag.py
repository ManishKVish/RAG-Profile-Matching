import unittest
from pathlib import Path
from resume_rag import VectorStore, DocumentChunker, MetadataExtractor, load_and_index_resumes
from job_matcher import JobMatcher

class TestRAGProfileMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).parent.parent
        cls.resumes_dir = cls.base_dir / "data" / "resumes"
        cls.vector_store = load_and_index_resumes(str(cls.resumes_dir))
        cls.matcher = JobMatcher(cls.vector_store)

    def test_metadata_extraction(self):
        sample_text = (
            "NAME: Alice Wonder\n"
            "TITLE: Senior Backend Architect\n"
            "EXPERIENCE: 8 years\n"
            "EDUCATION: M.S. in Computer Science\n"
            "SKILLS: Python, Go, Kubernetes, Kafka\n"
        )
        meta = MetadataExtractor.extract(sample_text)
        self.assertEqual(meta["name"], "Alice Wonder")
        self.assertEqual(meta["experience_years"], 8)
        self.assertIn("Python", meta["skills"])
        self.assertIn("Go", meta["skills"])

    def test_document_chunking_preserves_sections(self):
        sample_text = (
            "PROFESSIONAL SUMMARY:\nExperienced engineer.\n\n"
            "WORK EXPERIENCE:\nSenior Engineer at Tech Corp.\n\n"
            "EDUCATION:\nB.S. Computer Science."
        )
        chunks = DocumentChunker.chunk_document(sample_text, {"name": "Test"})
        sections = [c["section"] for c in chunks]
        self.assertIn("PROFESSIONAL SUMMARY", sections)
        self.assertIn("WORK EXPERIENCE", sections)
        self.assertIn("EDUCATION", sections)

    def test_job_matcher_output_format(self):
        jd = "Senior Machine Learning Engineer with Python, PyTorch, and Docker"
        result = self.matcher.match(
            job_description=jd,
            must_have_skills=["Python", "PyTorch", "Docker"],
            min_experience_years=5,
            top_k=5
        )

        # Assert brief format
        self.assertIn("job_description", result)
        self.assertIn("top_matches", result)
        self.assertGreaterEqual(len(result["top_matches"]), 1)

        first_match = result["top_matches"][0]
        self.assertIn("candidate_name", first_match)
        self.assertIn("resume_path", first_match)
        self.assertIn("match_score", first_match)
        self.assertIn("matched_skills", first_match)
        self.assertIn("relevant_excerpts", first_match)
        self.assertIn("reasoning", first_match)

        # Top match for ML should be John Doe
        self.assertEqual(first_match["candidate_name"], "John Doe")
        self.assertGreaterEqual(first_match["match_score"], 60)

    def test_must_have_filtering_penalty(self):
        jd = "Lead DevOps & Cloud Engineer with Kubernetes, Terraform, and CI/CD"
        result = self.matcher.match(
            job_description=jd,
            must_have_skills=["Kubernetes", "Terraform", "CI/CD"],
            min_experience_years=5,
            top_k=5
        )
        top_cand = result["top_matches"][0]["candidate_name"]
        self.assertEqual(top_cand, "Priya Sharma")

if __name__ == "__main__":
    unittest.main()
