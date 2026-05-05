import unittest
from unittest.mock import patch

from core.state import AgentState, CandidateProfileState
from agents.supervisor import run_graph
from data.models import DiscoveredPage


class GraphE2ESmokeTest(unittest.TestCase):
    @patch("agents.researcher_agent.fetch_pages")
    @patch("agents.researcher_agent.crawl_seed_urls")
    @patch("core.vector_store.JobVectorStore.similarity_search")
    @patch("core.vector_store.JobVectorStore.add_jobs")
    @patch("services.matching.job_matcher.JobMatcher._semantic_similarity")
    def test_graph_end_to_end(
        self,
        mock_similarity,
        mock_add_jobs,
        mock_search,
        mock_crawl,
        mock_fetch_pages,
    ):
        mock_crawl.return_value = ["https://example.com/careers/python"]
        mock_fetch_pages.return_value = [
            DiscoveredPage(
                source_url="https://example.com/careers/python",
                title="Senior Python Engineer",
                text="We are hiring. Apply here https://example.com/apply and email jobs@example.com. Skills Python AWS Docker",
                metadata={},
            )
        ]
        mock_add_jobs.return_value = 1
        mock_search.return_value = [
            {
                "job_id": "31a92c5a5c7d31a6e2bce26f211d2f440f1303e7",
                "document": "",
                "metadata": {},
                "distance": 0.1,
            }
        ]
        mock_similarity.return_value = 0.95

        profile = CandidateProfileState(
            name="Alex",
            email="alex@example.com",
            skills=["Python", "AWS", "Docker"],
            experience=["Backend engineering"],
            projects=["Job matcher"],
            cv_text="Python backend engineer",
        )

        state = AgentState(user_profile=profile)
        final_state = run_graph(state)
        state_dict = final_state if isinstance(final_state, dict) else final_state.model_dump()

        self.assertGreaterEqual(len(state_dict.get("deduped_jobs", [])), 1)
        self.assertGreaterEqual(len(state_dict.get("matched_jobs", [])), 1)
        self.assertIn("source_counts", state_dict.get("metrics", {}))


if __name__ == "__main__":
    unittest.main()
