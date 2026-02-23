# Morse Code Trainer

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![Tests](https://img.shields.io/badge/tests-337%20passing-brightgreen.svg)](#-testing)

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

High-quality Morse code audio powered by pygame-ce with custom WAV synthesis for authentic dit/dah tones.

> **Note**: Morse code audio file playback is not yet supported in Training and Testing modes. Audio is currently available only in Learning and Sandbox modes.

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
   pip install -r requirements.txt
   ```

   For development (includes pytest):

   ```bash
   pip install -r requirements-dev.txt
   ```

### Running the Application

```bash
python run.py
```

## 🧪 Testing

The project includes a comprehensive test suite with **337 tests** covering models, controllers, services, and utilities.

### Run Tests

```bash
cd src
pytest
```

### Run with Coverage Report

```bash
pytest --cov=main.python --cov-report=html
```

### HTML Test Report

After running tests, an HTML report is generated at `src/report.html`.

### Test Categories

| Category             | Description                         |
| -------------------- | ----------------------------------- |
| `tests/model/`       | Domain entities and session state   |
| `tests/controllers/` | Presenter logic and UI coordination |
| `tests/services/`    | Audio, data providers, settings     |
| `tests/utils/`       | Morse translator utilities          |
| `tests/resources/`   | Asset loading and constants         |

## 📁 Project Structure

```text
MorseCodeProgram/
├── run.py                    # Application entry point
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies (pytest)
├── LICENSE.md                # MIT License
├── README.md                 # This file
├── DEVPLAN.md                # Development roadmap
│
├── src/
│   ├── main/
│   │   ├── python/           # Application source code
│   │   │   ├── application.py
│   │   │   ├── main.py
│   │   │   ├── controllers/  # MVC presenters
│   │   │   ├── model/        # Domain entities & state
│   │   │   ├── services/     # Audio, data providers
│   │   │   ├── utils/        # Morse translator
│   │   │   └── views/        # CustomTkinter UI
│   │   │
│   │   └── resources/        # Audio files & assets
│   │       ├── letters/      # Letter audio files
│   │       ├── numbers/      # Number audio files
│   │       ├── symbols/      # Symbol audio files
│   │       ├── testing/      # Test audio prompts
│   │       └── translation/  # Translation assets
│   │
│   └── tests/                # pytest test suite
│       ├── conftest.py       # Shared fixtures
│       └── ...
│
└── output/                   # Generated files (exports, saves)
```

## 🏗️ Architecture

The application follows an **MVC-style architecture**:

- **Controllers** — Hold all domain logic, coordinate between models and views
- **Models** — Immutable state objects using frozen dataclasses
- **Views** — Presentation-only CustomTkinter components
- **Services** — Audio playback, data providers, settings management

### Key Design Decisions

- **Immutable State**: Models expose frozen dataclass states to prevent accidental mutation
- **Decoupled Audio**: pygame-ce integration is mocked in tests for CI stability
- **Theme Tokens**: Centralized font/color constants in `views/theme.py`
- **Componentized Views**: UI sections are modular for easy framework swaps

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
docker build -t morse-trainer .
docker run --rm morse-trainer

# Or using docker compose
docker compose run --rm test
```

### Development Shell

```bash
docker compose run --rm dev
```

### Run Application (Linux with X11)

```bash
xhost +local:docker
docker compose run --rm app
```

> **Note**: GUI applications in Docker require X11 forwarding. On Windows, use WSLg or VcXsrv.

## � Packaging & Releases

The application uses [Briefcase](https://briefcase.readthedocs.io/) to create native installers for all platforms.

### Build Locally

```bash
# Install Briefcase
pip install briefcase

# Create and build for your platform
briefcase create
briefcase build
briefcase run        # Test the built app
briefcase package    # Create installer
```

### Platform-Specific Outputs

| Platform | Command | Output |
| -------- | ------- | ------ |
| Windows | `briefcase package windows` | `.msi` installer |
| macOS | `briefcase package macOS --adhoc-sign` | `.dmg` disk image |
| Linux | `briefcase package linux appimage` | `.AppImage` portable |

### Automated Releases

Push a version tag to trigger automatic builds:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build installers for all platforms and create a release with downloadable assets.

### Adding Application Icons

Place your icons in `resources/icons/` (see [resources/icons/README.md](resources/icons/README.md) for required formats).

## 📋 Roadmap

See [DEVPLAN.md](DEVPLAN.md) for detailed development plans.

- [x] CI/CD pipeline with GitHub Actions
- [x] Docker containerization
- [x] Briefcase packaging and release automation
- [ ] Application icons
- [ ] Accessibility audit (keyboard navigation, light/dark modes)
- [ ] Custom deck import/export
- [ ] Analytics exports (CSV summaries)

## 🤝 Contributing

1. Fork the repository
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
