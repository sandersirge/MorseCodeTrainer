# DEVPLAN

## Current Status Snapshot

- UI modernisation complete across CustomTkinter views with stable audio integration
- Translation sandbox now provides segmented direction control, placeholders, and refreshed audio widgets
- Timed test workflow supports backward navigation, persistent answers, and pause exits through controller-model coordination
- Controllers hold all domain logic, models expose immutable state, and views stay presentation-only
- **Pytest coverage complete**: 337 tests across models, controllers, services, utils, and resources with HTML reporting
- **Project restructured**: `src/main/python/` for application code, `src/tests/` for test suite, `src/main/resources/` for assets
- **CI/CD configured**: GitHub Actions workflow runs tests on Python 3.10-3.12 across Ubuntu, Windows, macOS
- **Docker support added**: Dockerfile and docker-compose.yml for containerized testing and development
- **Packaging configured**: PyInstaller for standalone executables (Windows, macOS, Linux) with GitHub Actions release automation
- **Application icons added**: Full icon set generated (ICO, ICNS, PNG sizes) for all platforms

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

## Known Limitations

- Morse code audio playback not yet supported in Training and Testing modes (Sandbox only)

## Near-Term Priorities

- Add audio playback support to Training and Testing modes
- Audit accessibility: keyboard traversal, placeholder discoverability, and appearance toggles for light/dark modes
- Standardise error reporting with typed exceptions and presenter-to-view message mapping
- Add ruff linting/formatting to CI (currently runs but non-blocking)

## Longer-Term Goals

- Support custom deck import/export workflows while keeping controllers stateless
- Isolate CTk widget creation behind light factories to ease potential alternative front-end experiments
- Provide optional analytics exports (CSV summaries, instructor reports) without coupling to the UI layer

Revisit this plan when new stakeholder requirements arrive.
