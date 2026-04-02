# Morse Code Trainer

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Tests](https://img.shields.io/badge/tests-705%20passing-brightgreen.svg)](#-testing)

An interactive Morse code learning application built with Python and CustomTkinter. Learn Morse code through guided translations, flashcard drills, free-form practice, and timed assessments.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-blue)
![Pygame](https://img.shields.io/badge/Pygame-Audio-green)

## ✨ Features

### 🔤 Translation Training

Guided translation sessions with progress tracking, hints, and audio playback. Practice converting between plain text and Morse code with immediate feedback.

### 🃏 Flashcard Drills

Category-based flashcard decks covering letters, numbers, and symbols. Audio pronunciations help reinforce learning with progress indicators.

### 🎮 Sandbox Mode

Free-form translator for experimenting with Morse code. Features adjustable audio settings:

- Volume control
- Speed (WPM) adjustment
- Pitch customization
- Save and export options

### ⏱️ Timed Tests

Challenge yourself with randomized prompts, accuracy scoring, and detailed timing metrics. Supports:

- Words and sentences
- Backward navigation and answer persistence
- Pause/resume functionality

### 🔊 Audio Engine

High-quality Morse code audio powered by pygame-ce with custom WAV synthesis for authentic dit/dah tones. An `AudioCache` service synthesizes audio on demand and caches the result for the session:

- **Learning mode** — dynamic synthesis with static `.wav` file fallback
- **Translation exercises** (morse→text) — dynamic synthesis
- **Sandbox** — adjustable speed, pitch, and volume controls

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (tested up to 3.14)
- **pip** package manager
- **Windows/macOS/Linux** (GUI requires display)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sandersirge/MorseCodeProgram.git
   cd MorseCodeProgram
   ```

2. **Create and activate virtual environment**

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements/requirements.txt
   ```

   For development (includes pytest):

   ```bash
   pip install -r requirements/requirements-dev.txt
   ```

### Running the Application

```bash
python run.py
```

## 🧪 Testing

The project includes a comprehensive test suite with **705 tests** covering models, controllers, services, utilities, resources, and exceptions.

### Run Tests

```bash
cd src
pytest
```

### Run Only Smoke Tests (fast, < 1 s)

```bash
cd src
pytest -m smoke -q
```

### Run with Coverage Report

```bash
pytest --cov=main.python --cov-report=html
```

### HTML Test Report

After running tests, an HTML report is generated at `reports/report.html`.

### Test Categories

| Category                | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `tests/model/`          | Domain entities and session state                   |
| `tests/controllers/`    | Presenter logic and UI coordination                 |
| `tests/services/`       | Audio cache, data providers, settings               |
| `tests/utils/`          | Morse translator — unit, parametrized, and property |
| `tests/resources/`      | Asset loading and constants                         |
| `tests/exceptions/`     | Exception hierarchy, error codes, user messages     |
| `tests/application/`    | DI wiring and bootstrap integration                 |
| `tests/views/`          | Theme tokens, widget helpers, regressions           |
| `tests/test_smoke.py`   | Fast bootstrap sanity checks (`pytest -m smoke`)    |

## 📁 Project Structure

```text
MorseCodeProgram/
├── run.py                    # Application entry point
├── morsetrainer.spec         # PyInstaller build spec
├── pyproject.toml            # Project metadata and tool config
├── LICENSE.md                # MIT License
├── README.md                 # This file
├── DEVPLAN.md                # Development roadmap
│
├── docker/                   # Container configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements/             # Dependency files
│   ├── requirements.txt      # Runtime dependencies
│   └── requirements-dev.txt  # Development dependencies
│
├── reports/                  # Test report output (generated)
│
├── resources/
│   └── icons/                # Application icons (ICO, ICNS, PNG)
│
├── src/
│   ├── main/
│   │   ├── python/           # Application source code
│   │   │   ├── application.py    # App wiring & DI bootstrap
│   │   │   ├── main.py           # Entry point
│   │   │   ├── navigator.py      # Frozen routing dataclass
│   │   │   ├── view_stack.py     # Frame-swap navigation manager
│   │   │   ├── controllers/  # MVC presenters
│   │   │   │   ├── protocols.py      # Presenter Protocol types
│   │   │   │   ├── flashcard_controller.py
│   │   │   │   ├── translation_controller.py
│   │   │   │   ├── test_controller.py
│   │   │   │   └── translation_sandbox_controller.py
│   │   │   ├── exceptions/   # Typed exception hierarchy
│   │   │   │   ├── base.py       # ErrorCode, MorseTrainerError
│   │   │   │   ├── session.py
│   │   │   │   ├── translation.py
│   │   │   │   ├── audio.py
│   │   │   │   └── validation.py
│   │   │   ├── model/        # Domain entities & state
│   │   │   ├── resources/    # Constants & data tables
│   │   │   │   ├── morse_data.py     # Symbol tables & lookup maps
│   │   │   │   ├── audio_data.py     # Audio asset path maps
│   │   │   │   ├── exercise_data.py  # Training/test samples
│   │   │   │   └── constants.py      # Re-export shim
│   │   │   ├── services/     # Audio, data providers
│   │   │   │   ├── audio_cache.py    # Dynamic synthesis + cache
│   │   │   │   ├── morse_audio.py    # WAV synthesis engine
│   │   │   │   ├── audio_provider.py # pygame wrapper
│   │   │   │   ├── audio_settings.py # User preferences
│   │   │   │   └── data_provider.py  # Session factories
│   │   │   ├── utils/        # Morse translator
│   │   │   └── views/        # CustomTkinter UI
│   │   │       ├── theme.py          # get_colors(), callbacks
│   │   │       ├── widgets.py        # Shared UI components
│   │   │       └── ...               # Screen views
│   │   │
│   │   └── resources/        # Static audio files
│   │       ├── letters/      # Letter audio (.wav)
│   │       ├── numbers/      # Number audio (.wav)
│   │       └── symbols/      # Symbol audio (.wav)
│   │
│   └── tests/                # pytest test suite
│       ├── conftest.py       # Shared fixtures
│       ├── exceptions/       # Exception hierarchy tests
│       ├── test_smoke.py     # Bootstrap sanity checks
│       └── ...
│
└── output/                   # Generated files (exports, saves)
```

## 🏗️ Architecture

The application follows an **MVC-style architecture**:

- **Controllers** — Hold all domain logic, coordinate between models and views
- **Models** — Immutable state objects using frozen dataclasses
- **Views** — Presentation-only CustomTkinter components
- **Services** — Audio synthesis and caching, data providers, settings management

### Key Design Decisions

- **Navigator Pattern**: A frozen `Navigator` dataclass provides named `Callable` fields for all routes. Views depend on `Navigator` instead of individual callbacks — adding a screen only requires a new field
- **ViewStack Frame-Swap**: `ViewStack` registers a persistent `CTkFrame` per view. Navigation uses `pack_forget()`/`pack()` to swap visible frames — no widgets are destroyed on screen transitions
- **Protocol-Based Decoupling**: Views annotate presenter parameters with `Protocol` types from `controllers/protocols.py`. Concrete presenters satisfy protocols implicitly — no inheritance required
- **Dynamic Audio**: `AudioCache` synthesizes Morse audio on demand via `synthesize_morse_audio()`, caching results per session. Flashcard mode falls back to static `.wav` files; translation exercises use dynamic-only audio
- **Immutable State**: Models expose frozen dataclass states to prevent accidental mutation
- **Decoupled Audio**: pygame-ce integration is mocked in tests for CI stability
- **Theme Tokens**: Centralized font/color constants in `views/theme.py`; all views call `get_colors()` at render time for correct light/dark theming
- **Typed Exceptions**: `exceptions/` package provides an `ErrorCode` enum, Estonian user-facing messages, and a `get_user_message()` helper — no raw strings in error paths
- **Separated Resource Concerns**: `resources/` split into `morse_data`, `audio_data`, and `exercise_data` modules

## 🛠️ Development

### Code Style

- Python type hints throughout
- Frozen dataclasses for state
- No direct UI manipulation in controllers

### Adding Tests

Tests use pytest with fixtures defined in `src/tests/conftest.py`. Audio playback is automatically mocked.

```python
# Example test
def test_translation_session_advances(sample_translation_items):
    session = TranslationSession.create(sample_translation_items)
    assert session.current_index == 0
```

### Theme Customization

Edit `src/main/python/views/theme.py` to modify:

- Font families and sizes
- Color palette
- Widget presets

## 🐳 Docker

### Run Tests in Docker

```bash
# Build and run tests
docker build -t morse-trainer -f docker/Dockerfile .
docker run --rm morse-trainer

# Or using docker compose
docker compose -f docker/docker-compose.yml run --rm test
```

### Development Shell

```bash
docker compose -f docker/docker-compose.yml run --rm dev
```

### Run Application (Linux with X11)

```bash
xhost +local:docker
docker compose -f docker/docker-compose.yml run --rm app
```

> **Note**: GUI applications in Docker require X11 forwarding. On Windows, use WSLg or VcXsrv.

## 📦 Packaging & Releases

The application uses [PyInstaller](https://pyinstaller.org/) to create standalone executables for all platforms.

### Build Locally

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your platform
pyinstaller morsetrainer.spec

# The built application will be in dist/MorseCodeTrainer/
```

### Platform-Specific Outputs

| Platform | Architecture | Artifact |
| -------- | ------------ | -------- |
| Windows | x64 | `MorseCodeTrainer-windows-x64.zip` |
| Windows | x86 | `MorseCodeTrainer-windows-x86.zip` |
| macOS | arm64 (Apple Silicon) | `MorseCodeTrainer-macos-arm64.dmg` |
| Linux | x64 | `MorseCodeTrainer-linux-x64.tar.gz` |
| Linux | arm64 | `MorseCodeTrainer-linux-arm64.tar.gz` |

### Automated Releases

Push a version tag to trigger automatic builds:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build executables for all 5 platform/architecture combinations and create a release with:

- **Windows**: `.zip` archives (x64, x86)
- **macOS**: `.dmg` disk image (Apple Silicon)
- **Linux**: `.tar.gz` archives (x64, arm64)
- **checksums.txt**: SHA256 hashes for all assets

### Adding Application Icons

Place your icons in `resources/icons/` (see [resources/icons/README.md](resources/icons/README.md) for required formats).

## 📋 Roadmap

See [DEVPLAN.md](DEVPLAN.md) for detailed development plans.

- [x] CI/CD pipeline with GitHub Actions
- [x] Docker containerization
- [x] PyInstaller packaging and release automation
- [x] Multi-platform builds (Windows x64/x86, macOS arm64, Linux x64/arm64)
- [x] Application icons
- [x] Accessibility improvements (keyboard navigation, light/dark mode)
- [x] Typed exception hierarchy with Estonian user messages
- [x] Property-based tests with Hypothesis
- [x] Smoke test suite (`pytest -m smoke`)
- [x] Navigator routing & ViewStack frame-swap architecture
- [x] Protocol-based presenter decoupling
- [x] Dynamic audio synthesis via AudioCache
- [ ] Custom deck import/export
- [ ] Analytics exports (CSV summaries)

## 🤝 Contributing

1. Clone the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all tests pass before submitting.

## 📄 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.

## 🙏 Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI components
- [pygame-ce](https://github.com/pygame-community/pygame-ce) for audio playback
- The Morse code learning community
