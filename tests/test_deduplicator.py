import unittest

from utils.deduplicator import deduplicate_jobs


class DeduplicatorTests(unittest.TestCase):
    def test_deduplicate_jobs(self):
        rows = [
            {"source_url": "https://a.com/job1", "job_title": "Engineer", "company": "A"},
            {"source_url": "https://a.com/job1", "job_title": "Engineer", "company": "A"},
            {"source_url": "https://b.com/job2", "job_title": "Developer", "company": "B"},
        ]
        out = deduplicate_jobs(rows)
        self.assertEqual(len(out), 2)
        self.assertTrue(all("job_hash" in row for row in out))


if __name__ == "__main__":
    unittest.main()
