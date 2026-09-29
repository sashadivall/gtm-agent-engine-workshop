import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import gtm_agent


class TestRunAgent(unittest.TestCase):
    def test_email_request_uses_resolved_rep_in_prompt(self):
        fake_agent = Mock()
        fake_agent.invoke.return_value = {"messages": [Mock(content="sent")]}
        rep = {"rep_id": "rep_amills", "name": "Ava Mills", "email": "ava.mills@northpoint.com"}

        with patch.object(gtm_agent, "create_gtm_agent", return_value=fake_agent) as create_agent, \
                patch.object(gtm_agent.data_service, "get_rep", return_value=rep) as get_rep:
            gtm_agent.run_agent("Email LEAD-70001", user_id="rep_amills")

        prompt = create_agent.call_args.args[0]
        self.assertIn("Ava Mills", prompt)
        self.assertIn("ava.mills@northpoint.com", prompt)
        get_rep.assert_called_once_with("rep_amills")

    def test_scoring_request_does_not_require_current_rep_tool(self):
        fake_agent = Mock()
        fake_agent.invoke.return_value = {"messages": [Mock(content="score: 80")]}
        rep = {"rep_id": "rep_amills", "name": "Ava Mills", "email": "ava.mills@northpoint.com"}

        with patch.object(gtm_agent, "create_gtm_agent", return_value=fake_agent), \
                patch.object(gtm_agent.data_service, "get_rep", return_value=rep) as get_rep:
            result = gtm_agent.run_agent("Score LEAD-70001 against OFFER-10001", user_id="rep_amills")

        self.assertEqual(result["reply"], "score: 80")
        get_rep.assert_called_once_with("rep_amills")
