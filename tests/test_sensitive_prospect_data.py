import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service, gtm_agent


SENSITIVE_FIELDS = ("billing_qualification", "tax_id", "card_on_file", "date_of_birth")


class CaptureScoringLLM:
    def __init__(self):
        self.messages = None

    def invoke(self, messages):
        self.messages = messages
        return SimpleNamespace(model_dump=lambda: {"score": 50})


class SensitiveProspectDataTest(unittest.TestCase):
    def assert_does_not_contain_sensitive_fields(self, value):
        serialized = json.dumps(value)
        for field in SENSITIVE_FIELDS:
            self.assertNotIn(field, serialized)

    def test_prospect_tools_and_scoring_prompt_exclude_billing_data(self):
        prospect_id = "LEAD-12853"
        profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})
        contact = gtm_agent.get_prospect.invoke({"prospect_id": prospect_id})
        self.assert_does_not_contain_sensitive_fields(profile)
        self.assert_does_not_contain_sensitive_fields(contact)

        scoring_llm = CaptureScoringLLM()
        offering = data_service.get_offering("OFFER-10001")
        with patch.object(gtm_agent, "_scoring_llm", scoring_llm):
            gtm_agent.score_prospect.func(profile["prospect_profile"], offering)

        self.assert_does_not_contain_sensitive_fields(scoring_llm.messages)
