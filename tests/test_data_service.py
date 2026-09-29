import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class UpdateProspectInfoTest(unittest.TestCase):
    def setUp(self):
        self.original_tech_stack = list(data_service.PROSPECTS["LEAD-39002"]["tech_stack"])
        data_service.PROSPECTS["LEAD-39002"]["tech_stack"] = [
            technology for technology in self.original_tech_stack if technology != "Terraform"
        ]
        data_service._PROFILES.clear()

    def tearDown(self):
        data_service.PROSPECTS["LEAD-39002"]["tech_stack"] = self.original_tech_stack
        data_service._PROFILES.clear()

    def test_update_persists_to_source_and_cached_profile(self):
        build_prospect_profile.invoke({"prospect_id": "LEAD-39002"})

        data_service.update_prospect_info("LEAD-39002", "Terraform")

        self.assertIn("Terraform", data_service.fetch_tech_stack("LEAD-39002"))
        profile = build_prospect_profile.invoke({"prospect_id": "LEAD-39002"})["prospect_profile"]
        self.assertIn("Terraform", profile["tech_stack"])


if __name__ == "__main__":
    unittest.main()
