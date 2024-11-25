# Schulstick Portal App

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
- **Icon Finder**: Utility for theme icon discovery

## Development

The project uses Nix for reproducible builds and dependencies management.

### Quick Start

Run components directly using Nix:

```bash
# Run the welcome wizard
nix run .#welcome -L

# Run the portal app
nix run .#portal -L

# Run the vision assistant
nix run .#vision-assistant -L
```

### Development Environment

For development work, enter the development shell:

```bash
# Enter development environment
nix develop

# Then run components directly:
portal
welcome
vision-assistant
```

### Development Tools

Several utilities are available to help with development:

- **Icon Finder**: A utility to browse and search available theme icons
  ```bash
  nix run .#icon-finder -L
  ```

## License

This project is open source and part of the Schulstick initiative.
