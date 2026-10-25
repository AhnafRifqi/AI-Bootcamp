import unittest
from unittest.mock import patch

from app import router


class DetectIntentTests(unittest.TestCase):
    def test_ticket_id_routes_to_tool(self):
        self.assertEqual(router.detect_intent("Status TICKET-0001 saya?"), "ticket_status")

    def test_ticket_status_without_id_routes_to_tool(self):
        self.assertEqual(router.detect_intent("Tolong cek status tiket saya"), "ticket_status")

    def test_helpdesk_faq_routes_to_rag(self):
        self.assertEqual(
            router.detect_intent("Bagaimana cara reset password VPN?"),
            "faq",
        )

    def test_unrelated_message_is_unknown(self):
        self.assertEqual(router.detect_intent("Halo, apa kabar?"), "unknown")


class RouteTests(unittest.TestCase):
    @patch.object(router, "get_ticket_status", return_value=None)
    def test_unknown_ticket_uses_tool_and_returns_not_found(self, get_ticket_status):
        result = router.route("Cek status TICKET-9999")

        get_ticket_status.assert_called_once_with("TICKET-9999")
        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["intent"], "ticket_status")

    def test_unknown_intent_does_not_call_rag(self):
        with patch.object(router, "_get_index") as get_index:
            result = router.route("Halo")

        get_index.assert_not_called()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["intent"], "unknown")

    @patch.object(router, "generate_answer", return_value="Jawaban dari knowledge base.")
    @patch.object(
        router,
        "semantic_search",
        return_value=[{"faq_id": 1, "question": "Berapa jatah cuti tahunan?"}],
    )
    @patch.object(router, "_get_index", return_value=("index", "dataframe"))
    def test_faq_routes_to_rag(self, get_index, semantic_search, generate_answer):
        result = router.route("Berapa jatah cuti tahunan?")

        get_index.assert_called_once_with()
        semantic_search.assert_called_once_with("index", "dataframe", "Berapa jatah cuti tahunan?", top_k=3)
        generate_answer.assert_called_once()
        self.assertEqual(result["intent"], "faq")
        self.assertEqual(result["data"]["answer"], "Jawaban dari knowledge base.")


if __name__ == "__main__":
    unittest.main()
