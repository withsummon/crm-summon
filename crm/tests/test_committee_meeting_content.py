import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from crm.api.committee import generate_meeting_content, save_live_transcript_segment, set_live_transcript_bookmark


class TestCommitteeMeetingContent(TestCase):
	def test_live_segment_preserves_audio_source_and_bookmark(self):
		meeting = SimpleNamespace(transcript_json="[]", db_set=Mock())
		with patch("crm.api.committee._transcript_meeting", return_value=meeting), patch(
			"crm.api.committee.frappe", SimpleNamespace(session=SimpleNamespace(user="Administrator"))
		):
			segment = save_live_transcript_segment("CRM-COMM-TEST", "Pembahasan risiko", "mic", 1250)
			self.assertEqual(segment["speaker"], "Anda")
			self.assertEqual(segment["offset_ms"], 1250)
			meeting.transcript_json = meeting.db_set.call_args.args[1]
			bookmarked = set_live_transcript_bookmark("CRM-COMM-TEST", 0, True)
			self.assertTrue(bookmarked["bookmarked"])

	def test_analysis_uses_saved_transcript_and_persists_result(self):
		meeting = SimpleNamespace(
			title="Ulasan kredit",
			committee="Komite Kredit",
			agenda_json='[{"item":"Risiko kredit"}]',
			transcript_json='[{"text":"Risiko jaminan perlu ditinjau."}]',
			meeting_content_json="{}",
			db_set=Mock(),
		)
		with patch("crm.api.committee._transcript_meeting", return_value=meeting), patch(
			"crm.ai.openrouter.call_llm_chat", return_value=SimpleNamespace(content="Risiko belum diputuskan [segmen 1].")
		) as generate:
			result = generate_meeting_content("CRM-COMM-TEST", "analysis")

		self.assertEqual(result["transcript_count"], 1)
		self.assertIn("Risiko jaminan perlu ditinjau", generate.call_args.args[0][1]["content"])
		field, stored = meeting.db_set.call_args.args
		self.assertEqual(field, "meeting_content_json")
		self.assertEqual(json.loads(stored)["analysis"]["content"], result["content"])
