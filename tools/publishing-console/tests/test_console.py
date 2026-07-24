from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


CONSOLE = Path(__file__).resolve().parents[1]
ROOT = CONSOLE.parents[1]
sys.path.insert(0, str(CONSOLE))

import app as console_app  # noqa: E402
from page_data_registry import PageDataRegistry, SUPPORTED_ACTIVITY_TYPES  # noqa: E402


class PageDataRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = PageDataRegistry(ROOT, ROOT / "bcube-publishing-sdk/books/cover-books.json")

    def test_every_registered_book_has_44_resolvable_pages(self) -> None:
        books = json.loads(
            (ROOT / "bcube-publishing-sdk/books/cover-books.json").read_text(encoding="utf-8")
        )
        total = 0
        for level, level_data in books["levels"].items():
            for slug in level_data["books"]:
                pages = self.source.list_pages(level, slug)
                self.assertEqual(44, len(pages), f"{level}/{slug}")
                self.assertEqual(list(range(1, 45)), [page.physical_page for page in pages])
                self.assertEqual("cover", pages[0].page_type)
                for page in pages[1:]:
                    self.assertNotEqual("cover", page.page_type)
                    self.assertIn(page.activity_type, SUPPORTED_ACTIVITY_TYPES)
                    self.assertTrue(page.title)
                    self.assertTrue(page.objective)
                    self.assertTrue(page.instruction)
                    self.assertLessEqual(len(page.instruction), 220)
                total += len(pages)
        self.assertEqual(1320, total)

    def test_page_record_comes_from_exact_v4_package(self) -> None:
        page = self.source.get_page("ukg", "young-scientists", 8)
        self.assertEqual("YS-UKG-V4-P008", page.page_id)
        self.assertEqual(7, page.printed_page)
        self.assertTrue(page.printed_visible)
        self.assertIn("production-prompts/young-scientists/ukg/v4/pages/", page.source)

    def test_unknown_page_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "not registered"):
            self.source.get_page("ukg", "young-scientists", 45)


class PublishingConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        console_app.app.config.update(TESTING=True)
        self.client = console_app.app.test_client()

    def test_pages_endpoint_returns_resolved_metadata(self) -> None:
        response = self.client.get("/api/pages?level=ukg&book=young-scientists")
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        self.assertEqual(44, len(payload["pages"]))
        self.assertEqual("YS-UKG-V4-P002", payload["pages"][1]["page_id"])
        self.assertEqual("Hidden", payload["pages"][1]["printed_page_label"])

    @patch.object(console_app, "save_upload", return_value=Path("C:/tmp/illustration.png"))
    @patch.object(console_app.subprocess, "run")
    def test_publish_resolves_non_cover_server_side(self, run_mock, _upload_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess([], 0, "published", "")
        response = self.client.post("/api/publish", data={
            "level": "ukg",
            "book": "young-scientists",
            "physical_page": "8",
            "title": "CLIENT-SUPPLIED TITLE MUST BE IGNORED",
            "page_id": "CLIENT-SUPPLIED-ID",
            "approve": "false",
        })
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        command = run_mock.call_args.args[0]
        self.assertEqual("activity", command[command.index("--page") + 1])
        self.assertEqual("YS-UKG-V4-P008", command[command.index("--page-id") + 1])
        self.assertNotIn("CLIENT-SUPPLIED TITLE MUST BE IGNORED", command)
        self.assertNotIn("CLIENT-SUPPLIED-ID", command)
        self.assertEqual(payload["page"]["title"], command[command.index("--title") + 1])

    @patch.object(console_app, "save_upload", return_value=Path("C:/tmp/illustration.png"))
    @patch.object(console_app.subprocess, "run")
    def test_hidden_front_matter_uses_hidden_number_convention(self, run_mock, _upload_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess([], 0, "published", "")
        response = self.client.post("/api/publish", data={
            "level": "nursery",
            "book": "confidence-builders",
            "physical_page": "2",
            "approve": "false",
        })
        self.assertEqual(200, response.status_code)
        command = run_mock.call_args.args[0]
        self.assertEqual("0", command[command.index("--page-number") + 1])

    @patch.object(console_app, "save_upload", return_value=Path("C:/tmp/illustration.png"))
    @patch.object(console_app.subprocess, "run")
    def test_optional_approval_is_forwarded(self, run_mock, _upload_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess([], 0, "published", "")
        response = self.client.post("/api/publish", data={
            "level": "lkg",
            "book": "early-literacy-adventures",
            "physical_page": "8",
            "approve": "true",
            "reviewer": "Basavaraj",
        })
        self.assertEqual(200, response.status_code)
        command = run_mock.call_args.args[0]
        self.assertIn("--approve", command)
        self.assertEqual("Basavaraj", command[command.index("--reviewer") + 1])

    def test_page_outside_manifest_is_rejected_before_upload(self) -> None:
        response = self.client.post("/api/publish", data={
            "level": "ukg",
            "book": "young-scientists",
            "physical_page": "45",
            "approve": "false",
        })
        self.assertEqual(400, response.status_code)
        self.assertIn("not registered", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
