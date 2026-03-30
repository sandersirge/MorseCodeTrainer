# DEVPLAN

## Current Status Snapshot

- UI modernisation complete across CustomTkinter views with stable audio integration
- Translation sandbox now provides segmented direction control, placeholders, and refreshed audio widgets
- Timed test workflow supports backward navigation, persistent answers, and pause exits through controller-model coordination
- Controllers hold all domain logic, models expose immutable state, and views stay presentation-only
- **Pytest coverage complete**: 638 tests across models, controllers, services, utils, resources, and exceptions with HTML reporting
- **Project restructured**: `src/main/python/` for application code, `src/tests/` for test suite, `src/main/resources/` for assets
- **CI/CD configured**: GitHub Actions workflow runs tests on Python 3.10-3.12 across Ubuntu, Windows, macOS
- **Docker support added**: Dockerfile and docker-compose.yml for containerized testing and development
- **Packaging configured**: PyInstaller for standalone executables (Windows, macOS, Linux) with GitHub Actions release automation
- **Application icons added**: Full icon set generated (ICO, ICNS, PNG sizes) for all platforms
- **Accessibility improvements**: Light/dark mode toggle, keyboard navigation helpers, focus indicators, and entry field placeholders
- **Error handling standardised**: Typed exception hierarchy with Estonian user messages; `get_user_message()` helper for views
- **Dynamic theming**: All views now use `get_colors()` for theme-aware rendering; light/dark mode applies across entire app
- **Ruff linting enforced**: Blocking ruff check and format in CI; tab-indented code style with UP/I/F/E/W rules

## Completed

- [x] Add pytest coverage for TestSession, translation presenters, and audio helpers; include pygame mocks for CI stability
- [x] Restructure project layout (src/main/python, src/tests, src/main/resources)
- [x] Configure pytest with HTML reporting and warning filters
- [x] Extract shared font and colour tokens into a theme helper to reduce duplication across CTk views
- [x] Add requirements.txt and requirements-dev.txt for dependency management
- [x] Create comprehensive README with badges, installation, and architecture documentation
- [x] Add MIT License
- [x] Configure GitHub Actions CI pipeline (multi-OS, multi-Python version matrix)
- [x] Add Docker support (Dockerfile, docker-compose.yml, .dockerignore)
- [x] Configure PyInstaller packaging (morsetrainer.spec, release workflow)
- [x] Add GitHub Actions release workflow for automated builds on tags
- [x] Add application icons (ICO for Windows, ICNS for macOS, sized PNGs for Linux)
- [x] Create morsetrainer wrapper package for packaging compatibility
- [x] Accessibility audit: light/dark mode toggle, keyboard navigation, focus indicators, placeholder text
- [x] Standardise error reporting with typed exceptions (`src/main/python/exceptions.py`) and Estonian user messages
- [x] Extend theme system to all views (flashcard, test, translation) using dynamic `get_colors()` API
- [x] Add ruff linting/formatting to CI as blocking checks (tab-style, pyproject.toml configured)
- [x] Remove `application_controller.py` / `MorseApp` stub (zero callers; `main.py` imports `application.py` directly)
- [x] Convert `exceptions.py` into `exceptions/` sub-package (`base.py`, `session.py`, `translation.py`, `audio.py`, `validation.py`, `__init__.py` re-export shim)
- [x] Split `translation_sandbox_sections.py` (635 lines) into `views/translation_section.py` + `views/audio_section.py` + shim
- [x] Split `constants.py` (255 lines) into `resources/morse_data.py`, `resources/audio_data.py`, `resources/exercise_data.py` + re-export shim
- [x] Add `tests/exceptions/` test suite (102 tests covering `ErrorCode`, `MorseTrainerError`, all exception subclasses)
- [x] Add parametrized tests for full Morse alphabet, digits, symbols in `test_morse_translator_parametrized.py`
- [x] Add Hypothesis property-based tests for encode→decode round-trip in `test_morse_translator_property.py`
- [x] Add smoke test suite (`tests/test_smoke.py`, `pytest.mark.smoke`) — 16 tests, completes in < 0.5 s

## Known Limitations

- Morse code audio playback not yet supported in Training and Testing modes (Sandbox only)

## Near-Term Priorities

- Add audio playback support to Training and Testing modes

## Architecture & Modularity Improvements

Issues identified across the current codebase. Ordered roughly by impact vs effort.

### 1. Retire static theme constants from `theme.py`

`theme.py` exports a backwards-compatible block of module-level constants (`TEXT_PRIMARY`, `BACKDROP_BG`, `CARD_BG`, etc.) that are always dark-mode values. These are the root cause of recurring light-mode colour bugs — any file that imports them statically gets the wrong colour in light mode. `widgets.py` still uses several of them in `BUTTON_STYLES`.

**Fix:** remove the static constant block entirely; replace every remaining import site with `get_colors()` calls. The `# Backwards-compatible module-level constants` section in `theme.py` and the corresponding imports in `widgets.py` (`SURFACE_ACCENT`, `SURFACE_DARK`, `TEXT_PRIMARY`, `TEXT_DARK`) should all be eliminated.

### 2. Make `BUTTON_STYLES` theme-aware

`widgets.py` defines `BUTTON_STYLES` as a module-level `dict[str, ButtonStyle]` with hardcoded hex strings. The `muted` and `ghost` variants use dark-mode hover colours (`"#141f33"`, `"#1e293b"`) that are invisible in light mode. `make_button` reads this dict once at call time, so theme changes are never reflected.

**Fix:** Convert to a function `get_button_style(variant: str) -> ButtonStyle` that calls `get_colors()` internally for the variants whose colours depend on the theme (muted, ghost, secondary). Purely accent-based variants (primary, danger, positive) can remain static.

### 3. Introduce a `Navigator` abstraction to replace manual routing in `Application`

`Application` currently acts as a manual router with individual navigation methods (`avalehekülg`, `tutvustus`, `režiim1`, `režiim2`, etc.). Each method redundantly resets all state. Every new screen requires modifying `Application` directly. Views receive navigation callbacks as positional `Callable` arguments, making intent opaque.

**Fix:** Extract a `Navigator` Protocol (or simple dataclass of named callables) and pass one `Navigator` instance to each view instead of a growing list of individual callbacks. `Application.attach_views()` becomes a one-liner that wires a `Navigator` to each view. Adding a screen no longer requires touching `Application`.

### 4. Replace `clear_screen()` with a view-stack / frame-swap pattern

`clear_screen()` destroys every child widget of the root window on every navigation. This is the root cause of `TclError` timing issues we have patched with `after_idle` workarounds, and it forces full widget rebuilds on every navigation, discarding all widget state.

**Fix:** Keep each view's top-level `CTkFrame` alive and use `.pack_forget()` / `.pack()` (or grid show/hide) to switch between screens. Views that need fresh state on entry can reset their own internal state in a `on_enter()` hook rather than rebuilding from scratch. This eliminates the TclError class entirely.

### 5. Define presenter `Protocol` types so views depend on abstractions

Views currently receive concrete presenter instances (`FlashcardPresenter`, `TranslationPresenter`, etc.), coupling the view layer directly to controller implementations. This makes substituting test doubles in integration tests awkward and prevents alternative presenter implementations.

**Fix:** Add `FlashcardPresenterProtocol`, `TranslationPresenterProtocol`, `TestPresenterProtocol`, `SandboxPresenterProtocol` as `typing.Protocol` classes in a `controllers/protocols.py` module. Views annotate their `presenter` arguments with these protocol types. Concrete controller classes implicitly satisfy them — no inheritance required.

### 6. ~~Split `translation_sandbox_sections.py` into two modules~~ ✅ DONE

Split into `views/translation_section.py` and `views/audio_section.py`. `translation_sandbox_sections.py` is now a 14-line re-export shim.

### 7. ~~Remove `application_controller.py` / `MorseApp` stub~~ ✅ DONE

Deleted `application_controller.py`. `main.py` already imported from `application.py` directly.

### 8. ~~Split `constants.py` by concern~~ ✅ DONE

Split into `resources/morse_data.py`, `resources/exercise_data.py`, and `resources/audio_data.py`. `constants.py` is now a re-export shim.

### 9. ~~Convert `exceptions.py` into a sub-package~~ ✅ DONE

`exceptions.py` is 357 lines containing five independent exception groups (session, translation, audio, validation, resource), the `ErrorCode` enum, `ErrorMessage` dataclass, the internal `_ERROR_MESSAGES` map, and the `get_user_message()` helper. These groups have no inter-group dependencies; they share the file only by convention.

**Fix:** Convert to a package at `exceptions/`:

```txt
exceptions/
    __init__.py          ← re-exports the full __all__ for zero-diff imports
    base.py              ← ErrorCode, ErrorMessage, MorseTrainerError, _ERROR_MESSAGES, get_user_message
    session.py           ← SessionError, SessionNotInitializedError, SessionInvalidStateError
    translation.py       ← TranslationError, UnsupportedCharacterError, UnsupportedMorseSymbolError, EmptyInputError
    audio.py             ← AudioError, NoAudioContentError, AudioSynthesisError, AudioSaveError
    validation.py        ← ValidationError, InvalidModeError, MismatchedDataError
```

All existing `from ..exceptions import X` call sites continue to work without modification because `exceptions/__init__.py` re-exports the complete `__all__`. The individual sub-modules can then be imported directly in tests (e.g. `from ..exceptions.audio import AudioSynthesisError`) for isolation.

---

## Test Coverage & Test Types

### Current state

The test suite has 337 unit tests covering: model layer (3 files), controller layer (4 files), services (3 files), utils (1 file), resources (1 file). All tests are plain pytest unit tests using `unittest.mock`. No specialised test types, no coverage reporting, and the following source modules have **zero test coverage**:

| Untested module | What is missing |
| --- | --- |
| `exceptions.py` | No tests for `ErrorCode`, `MorseTrainerError.__str__`, `user_message` fallback logic, exception hierarchies, `get_user_message()` |
| `application.py` | No tests for `build_application()` wiring, `Application.attach_views()`, `clear_screen()`, or navigation routing methods |
| `controllers/application_controller.py` | `MorseApp.bootstrap()` and `MorseApp.run()` untested |
| `views/theme.py` | `set_appearance_mode()`, `toggle_appearance_mode()`, `register_theme_callback()`, `get_colors()` all untested |
| `views/widgets.py` | `setup_keyboard_navigation()`, `add_focus_highlight()`, `make_button()`, `make_label()`, all font helpers untested |
| `services/audio_provider.py` | Pygame wrapper and import shim untested |

### 1. ~~Add `tests/exceptions/` test suite~~ ✅ DONE

Added 102 tests in `src/tests/exceptions/` mirroring the package structure (`test_base.py`, `test_session.py`, `test_translation.py`, `test_audio.py`, `test_validation.py`).

### 2. Add `tests/application/` integration test suite

`application.py` wires every presenter and view together through `build_application()` and `_build_views()`. No test currently exercises this path, meaning the app's DI wiring is only validated at runtime.

**Add:** `src/tests/application/test_wiring.py` — smoke tests that call `build_application()` with a mocked `root_factory` (returns a `Mock()` instead of `ctk.CTk`), assert all presenters are non-`None`, assert `attach_views()` sets all view references on the `Application` instance.

### 3. Add `tests/views/` for theme and widget helpers

`views/theme.py` and `views/widgets.py` contain testable pure logic (colour resolution, font construction, callback registration) that doesn't need a real Tk window.

**Add:** `src/tests/views/test_theme.py` — tests for `get_colors()` returning correct palette per mode, `set_appearance_mode()` normalising unknown values to `"dark"`, and `register_theme_callback()` / `unregister_theme_callback()` round-trip. `src/tests/views/test_widgets.py` — tests for `BUTTON_STYLES` key coverage, `make_font()` returning a `CTkFont`, `add_focus_highlight()` not raising on a widget with no border.

### 4. ~~Introduce parametrized tests for the translator and model boundaries~~ ✅ DONE

Several existing test classes test one input at a time for what are fundamentally data-driven cases. The full Morse alphabet (26 letters + digits + symbols) and all model state transitions (empty → first, last → wrap, previous at start) are natural candidates for `@pytest.mark.parametrize`.

**Refactor examples:**

```python
# Currently: separate methods per letter
def test_a_encodes_correctly(self): ...
def test_b_encodes_correctly(self): ...

# Better: parametrized
@pytest.mark.parametrize("letter,expected", consts.LETTER_MORSE_PAIRS)
def test_all_letters_encode_correctly(self, letter, expected): ...
```

This replaces implicit repetition with explicit data, makes gaps visible, and reduces line count.

### 5. ~~Add property-based tests with Hypothesis~~ ✅ DONE

`MorseTranslator` has a natural encode→decode round-trip property: any string composed of supported characters, encoded to Morse and decoded back, should equal the original (case-normalised). This class of test finds edge cases that hand-written parametrize lists miss.

**Install:** `hypothesis` as a dev dependency.

**Add:** `src/tests/utils/test_morse_translator_property.py`:

```python
from hypothesis import given, strategies as st
from src.main.python.utils.morse_translator import MorseTranslator

SUPPORTED_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"

@given(st.text(alphabet=SUPPORTED_CHARS, min_size=1, max_size=40))
def test_encode_decode_roundtrip(text):
    result = MorseTranslator.decode(MorseTranslator.encode(text))
    assert result.lower() == text.lower()
```

### 6. ~~Add smoke tests marked with `pytest.mark.smoke`~~ ✅ DONE

Fast sanity tests for CI that validate the app can bootstrap without errors, all exception types can be raised, and no import-time side-effects break the module graph. These should complete in under 1 second and can run as a separate CI step before the full suite.

**Add:** `pyproject.toml` marker registration:

```toml
[tool.pytest.ini_options]
markers = ["smoke: fast bootstrap sanity checks"]
```

CI step: `pytest -m smoke` before the full `pytest` run.

### 7. Add regression tests for fixed bugs

Known bugs that have been fixed (TclError on theme toggle, `make_label` static colour in light mode) should have regression tests so they cannot silently reappear. These live in their closest unit test module with a `# regression:` comment and a reference to the original issue.

---

## Longer-Term Goals

- Support custom deck import/export workflows while keeping controllers stateless
- Provide optional analytics exports (CSV summaries, instructor reports) without coupling to the UI layer

Revisit this plan when new stakeholder requirements arrive.
