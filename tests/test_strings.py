"""The UI text catalog is complete and every lookup in the code resolves."""

import ast
import string
from pathlib import Path

import pytest

from morsetrainer import strings
from morsetrainer.strings import ET, set_language, t

APP_DIR = Path(__file__).resolve().parents[1] / "src" / "morsetrainer"


def _used_keys() -> dict[str, list[str]]:
	"""Map every t("literal") key in the app code to the keyword names passed."""
	used: dict[str, list[str]] = {}
	for path in APP_DIR.rglob("*.py"):
		for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
			if (
				isinstance(node, ast.Call)
				and isinstance(node.func, ast.Name)
				and node.func.id == "t"
				and node.args
				and isinstance(node.args[0], ast.Constant)
			):
				used[node.args[0].value] = sorted(k.arg for k in node.keywords if k.arg)
	return used


def _placeholders(text: str) -> list[str]:
	return sorted({name for _, name, _, _ in string.Formatter().parse(text) if name})


class TestCatalog:
	def test_every_used_key_exists(self):
		missing = sorted(set(_used_keys()) - set(ET))
		assert missing == []

	def test_every_key_is_used(self):
		unused = sorted(set(ET) - set(_used_keys()))
		assert unused == []

	def test_values_passed_match_placeholders(self):
		for key, keywords in _used_keys().items():
			assert keywords == _placeholders(ET[key]), key

	def test_texts_are_not_empty(self):
		assert all(text.strip() for text in ET.values())


class TestLookup:
	def test_plain_lookup(self):
		assert t("common.tagasi_avalehele") == "Tagasi avalehele"

	def test_formatting(self):
		assert t("common.progress", percent=12.345) == "12.3% läbitud"
		assert t("common.question_counter", number=3, total=20) == "Küsimus 3/20"

	def test_unknown_key_raises(self):
		with pytest.raises(KeyError):
			t("no.such.key")

	def test_set_language_with_fallback(self):
		try:
			set_language({"common.tagasi": "Back"})
			assert t("common.tagasi") == "Back"
			assert t("common.tagasi_avalehele") == "Tagasi avalehele"  # falls back
		finally:
			set_language(strings.ET)
