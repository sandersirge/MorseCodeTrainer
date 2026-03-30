"""Re-export shim retained for import compatibility.

Content has been split into:
    views/translation_section.py  - TranslationSection
    views/audio_section.py        - AudioSection, SliderBinding
"""

from __future__ import annotations

from .audio_section import AudioSection, SliderBinding
from .translation_section import TranslationSection

__all__ = ["TranslationSection", "AudioSection", "SliderBinding"]
