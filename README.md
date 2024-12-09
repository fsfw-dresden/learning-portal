# Schulstick Portal App
![Release Workflow](https://github.com/fsfw-dresden/schulstick-portal/actions/workflows/release.yml/badge.svg?event=push)

An open educational portal app integrated into the "Schulstick" free software platform, designed to facilitate IT competency through interactive learning with complex computer programs. The project aims to promote interest in STEM subjects and ensure confident, curious, and sovereign handling of IT.

## Overview

Many students struggle with finding documentation, tutorials, or example files and learning programs independently. The Portal App serves as a central self-learning tool that addresses these challenges by:

- Making existing learning content (instructions, tutorial videos) easily discoverable
- Providing interactive courses with step-by-step instructions within running programs
- Enabling self-paced learning, especially beneficial for interested children in rural areas without access to Schulstick working groups

## Features

- Centralized access to curated OER learning materials
- Interactive step-by-step tutorials
- Integration with running applications
- Multi-language support (German/English)
- Cross-platform compatibility

## Components

- **Welcome Wizard**: Initial setup and user preference configuration
- **Vision Assistant**: Interactive guidance system
- **Portal Interface**: Central hub for accessing learning materials
- **Tutor**: Interactive tutorial and lecture system
- **Icon Finder**: Utility for theme icon discovery

## Development

The project uses Nix for reproducible builds and dependencies management.

### Example OER Materials

The `OER-materials` directory contains example courses. Learning units are organized in markdown files under `OER-materials/examples/[course_name]/[lesson_name]/`, for example:

- `OER-materials/examples/audacity/lektion4/mixing.md` - Audio mixing tutorial for Audacity
- `OER-materials/examples/inkscape/lektion1/intro.md` - Introduction to Inkscape

To serve the exampe courses during development, run the following command:

```bash
npx @liascript/devserver --live --input ./OER-materials
```

### Quick Start

Run components directly using Nix:

```bash
# Run the welcome wizard
nix run .#welcome -L

# Run the portal app
nix run .#portal -L

# Run the vision assistant
nix run .#vision-assistant -L

# Run the tutor
nix run .#tutor -L -- ./path/to/tutorial
```

### Development Environment

#### Using Nix

For development work using Nix, enter the development shell:

```bash
# Enter development environment
nix develop

# Then run components directly:
portal
welcome
tutor ./path/to/tutorial
vision-assistant

```

#### Using Python venv

Alternatively, you can use Python's virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package in editable mode
pip install -e .

# Run components
python -m portal.main
python -m welcome.main
python -m vision_assistant.main
```

### Development Tools

Several utilities are available to help with development:

- **Icon Finder**: A utility to browse and search available theme icons
  ```bash
  nix run .#icon-finder -L
  ```

- **Release Helper**: A tool to manage version releases
  ```bash
  # Create a new patch release (default)
  nix run .#release -L
  
  # Create a minor or major release
  nix run .#release -L minor
  nix run .#release -L major
  ```
  
  The release helper will:
  - Bump version numbers in pyproject.toml and flake.nix
  - Generate changelog from git commits (using Claude AI if ANTHROPIC_API_KEY is set)
  - Update CHANGELOG.md and debian/changelog
  - Create a git tag (requires manual push)

## License

This project is open source and part of the Schulstick initiative.
