import unittest

from data.models import DiscoveredPage
from services.parsing.hiring_signal_detector import detect_hiring_signal
from services.parsing.job_extractor import extract_job_record


class ParsingSmokeTests(unittest.TestCase):
    def test_signal_detector(self):
        signal = detect_hiring_signal("We are hiring a Python engineer. Apply here.")
        self.assertTrue(signal.is_hiring)
        self.assertGreaterEqual(signal.confidence_score, 0.3)

    def test_extractor(self):
        page = DiscoveredPage(
            source_url="https://example.com/careers/python",
            title="Senior Python Engineer",
            text=(
                "Join our team at ExampleCorp. "
                "Send your CV to jobs@example.com. "
                "Apply here https://example.com/apply/python. "
                "Skills: Python, Docker, AWS."
            ),
        )
        signal = detect_hiring_signal(page.text)
        job = extract_job_record(page, signal)
        self.assertEqual(job.job_title, "Senior Python Engineer")
        self.assertIn("python", job.skills)
        self.assertEqual(job.application_method["email"], "jobs@example.com")
        self.assertEqual(job.source_type, "company_careers")


if __name__ == "__main__":
    unittest.main()
