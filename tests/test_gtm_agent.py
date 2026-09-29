import unittest
import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")
from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    def test_disqualified_prospect_is_blocked_without_message_id(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Priya Nair",
                "email": "priya.nair@brightwaveapps.com",
                "disqualified": False,
            },
            "Checking in",
            "Hello",
            SimpleNamespace(config={}),
        )

        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("message_id", result)

    def test_qualified_prospect_is_sent(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-12853",
                "name": "Omar Okafor",
                "email": "omar.okafor@lakesideanalytics.com",
            },
            "Checking in",
            "Hello",
            SimpleNamespace(config={}),
        )

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)


if __name__ == "__main__":
    unittest.main()
