"""Tests for AudioCache service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from src.main.python.services.audio_cache import AudioCache


class TestAudioCacheResolve:
	"""Tests for resolve() — dynamic synthesis."""

	def test_resolve_returns_path_string(self):
		cache = AudioCache()
		result = cache.resolve(".-", "A")
		assert isinstance(result, str)
		assert result.endswith(".wav")
		Path(result).unlink(missing_ok=True)

	def test_resolve_caches_result(self):
		cache = AudioCache()
		first = cache.resolve(".-", "A")
		second = cache.resolve(".-", "A")
		assert first == second
		Path(first).unlink(missing_ok=True)

	def test_resolve_different_keys_produce_different_files(self):
		cache = AudioCache()
		a = cache.resolve(".-", "A")
		b = cache.resolve("-...", "B")
		assert a != b
		Path(a).unlink(missing_ok=True)
		Path(b).unlink(missing_ok=True)

	def test_resolve_returns_none_on_error(self):
		cache = AudioCache()
		result = cache.resolve("", "empty")
		assert result is None

	def test_resolve_returns_none_for_invalid_morse(self):
		cache = AudioCache()
		result = cache.resolve("XYZ", "bad")
		assert result is None


class TestAudioCacheResolveWithFallback:
	"""Tests for resolve_with_fallback() — dynamic then static."""

	def test_fallback_returns_dynamic_when_available(self):
		static = {"A": "/static/A.wav"}
		cache = AudioCache(static_map=static)
		result = cache.resolve_with_fallback(".-", "A")
		assert result is not None
		assert result != "/static/A.wav"
		Path(result).unlink(missing_ok=True)

	def test_fallback_uses_static_on_synthesis_failure(self):
		static = {"empty": "/static/empty.wav"}
		cache = AudioCache(static_map=static)
		with patch.object(cache, "resolve", return_value=None):
			result = cache.resolve_with_fallback("", "empty")
		assert result == "/static/empty.wav"

	def test_fallback_returns_none_when_both_miss(self):
		cache = AudioCache()
		result = cache.resolve_with_fallback("", "missing")
		assert result is None


class TestAudioCacheCleanup:
	"""Tests for cleanup() — temp file deletion."""

	def test_cleanup_deletes_cached_files(self):
		cache = AudioCache()
		path_str = cache.resolve(".-", "A")
		assert path_str is not None
		assert Path(path_str).exists()
		cache.cleanup()
		assert not Path(path_str).exists()

	def test_cleanup_clears_cache_dict(self):
		cache = AudioCache()
		cache.resolve(".-", "A")
		cache.cleanup()
		assert len(cache._cache) == 0

	def test_cleanup_on_empty_cache_is_safe(self):
		cache = AudioCache()
		cache.cleanup()  # should not raise

	def test_cleanup_tolerates_already_deleted_files(self):
		cache = AudioCache()
		path_str = cache.resolve(".-", "A")
		Path(path_str).unlink()
		cache.cleanup()  # should not raise


class TestAudioCacheInit:
	"""Tests for AudioCache construction."""

	def test_default_static_map_is_empty(self):
		cache = AudioCache()
		assert cache._static_map == {}

	def test_static_map_stored(self):
		static = {"X": "/x.wav"}
		cache = AudioCache(static_map=static)
		assert cache._static_map["X"] == "/x.wav"
