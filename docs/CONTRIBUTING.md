# Contributing

Thanks for helping improve GaleFling. This guide covers development setup, testing, and releases.

## Prerequisites

- Python 3.11+
- pip
- Windows for building the installer

## Setup

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run

```bash
make run
# or
python src/main.py
```

## Lint & Test

```bash
make lint
make test
make test-cov
```

## Build

```bash
make build
make installer
```

## Release Process

1. Bump the version in:
   - `src/utils/constants.py`
   - `resources/default_config.json`
   - `build/version_info.txt`
   - `build/installer.nsi`
2. Add an entry to `CHANGELOG.md`
3. Update `README.md` if user-facing behavior changed
4. Commit, tag, and push:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. The GitHub Action builds a Windows executable and publishes a **pre-release** with the installer attached.

## Project Structure

```
galefling/
├── src/
│   ├── main.py                      # Application entry point
│   ├── gui/                         # GUI layer
│   ├── platforms/                   # Platform integrations
│   ├── core/                        # Core services
│   └── utils/                       # Constants/helpers
├── infrastructure/                  # Log upload backend
├── resources/                       # Icons/config templates
├── tests/                           # Test suite
├── build/                           # Build scripts
└── .github/workflows/               # CI/CD
```
