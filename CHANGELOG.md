# 0.1.6 (2025-06-07)

## Summary
This release brings significant improvements to the portal's publishing capabilities, enhanced form handling, and better course management features. It also introduces a new translation system and improves the user interface with better theme support and navigation.

## Features
- Added a complete course publishing system with SSH key management and remote repository support
- Implemented a new translation management system for all modules (portal, tutor, welcome, vision assistant)
- Added a course editor with advanced form generation capabilities
- Introduced new course and lesson metadata handling
- Added view switching between Unit Finder and Unit Browser
- Implemented course collections and improved course display
- Added play button overlay for lesson playback
- Added "Open Folder" action to unit context menu
- Added reload button to rescan units collection
- Added lesson creation with directory and markdown template generation

## Fixes
- Improved dark/light theme compatibility for labels and buttons
- Fixed SSH key selection and wizard finish button issues
- Resolved various form generator issues with nested dataclasses
- Fixed web view resource cleanup on close
- Corrected default Gitolite username configuration
- Fixed editor URL configuration issues
- Improved UI responsiveness by moving publishing to background thread

## Other Changes
- Added Wayland detection and warning dialog
- Updated nixpkgs to version 24.11
- Added flake8 for improved code quality checks
- Improved code organization and removed unused code
- Enhanced form field validation and metadata handling

# 0.1.5 (2024-12-11)

## Summary

This changelog covers a range of improvements to the portal, including the ability to reload the units collection, create new lessons with a markdown template, and open unit lessons in the LiaScript editor. Several bug fixes and enhancements to the user interface have also been made.

## Features

- Added a "Reload" button to the portal toolbar to rescan the units collection
- Implemented lesson creation with a directory and markdown template generation
- Added a "Plus" button to the toolbar with a unit creation form
- Introduced LiaScript editor URL and open command configuration options
- Added a context menu with an "Open in Editor" option for unit cards

## Fixes

- Replaced `course.name` with `course.title` in the `UnitCreateForm`
- Various small fixes

## Other Changes

- None

# 0.1.4 (2024-12-11)

## Summary

This changelog covers a range of improvements to the learning portal application, including the addition of a desktop file and logo, a program launch confirmation dialog, and better handling of window closing and process termination. Several bug fixes have also been implemented, such as ensuring that the tutor application only opens once. It fixes the loading of single units without metadata.

## Features

- Added a desktop file, wrapper script, and logo to the application, improving the user experience.
- Implemented a program launch confirmation dialog, providing users with more control over the application's startup.
- Introduced the TutorViewProxy using the Virtual Proxy pattern, simplifying the management of TutorView instances.
- Added a close button to the context menu, giving users a more intuitive way to exit the application.

## Fixes

- Enabled recursive submodules in the release workflow, ensuring that all necessary components are included in the deployment.
- Allowed lesson metadata to be called `metadata.yml`, providing more flexibility in how this information is stored.
- Implemented better singleton management and window close handling in the TutorView, preventing multiple instances from running simultaneously.

## Other Changes

- Added submodules for `schulstick-tutorial-docs` and `Jan_Maul_Blender`, expanding the content available to users.

# 0.1.3 (2024-12-09)

## Summary

This changelog covers a range of changes to the unit scanner and lesson loading functionality, including improvements to the portal window, unit card display, and Debian packaging. Additionally, some refactoring and cleanup tasks have been completed.

## Features

- Added `SimpleUnitCard` for displaying simple markdown lessons
- Added warnings for missing `content.md` and multiple markdown files
- Implemented fallback to first markdown file if `content.md` is missing
- Refactored unit scanner to support new course and lesson structure

## Fixes

- Launched portal correctly
- Resolved flake8 errors in unit scanner method calls
- Resolved Path serialization and content file loading issues in unit scanner
- Fixed Blender sample unit
- Addressed issues with Debian packaging, including removing `python3-yaml` dependency and setting `PYTHONPATH` for `pip3 install`

## Other Changes

- Increased portal window default size
- Finalized unit scanning mechanism and settings (one base unit path only)
- Renamed `metatdata.yml` to `lesson.yml`
- Improved lesson loading and validation in unit scanner
- Removed `tutor-next` things and used new folder structure
- Cleaned up build artifacts and temporary directories in `debian/rules`

# 0.1.2 (2024-11-28)

## Summary

Mainly work on TutorView and configuration system improvements. Added configuration management, unit scanning enhancements,
and LiaScript integration. Also improved link handling, view modes, and orientation support.

## Features

- Added configuration system with environment-aware loading and default settings
- Implemented config system using dataclass_wizard for YAML serialization
- Added program launcher and auto-launch functionality for units
- Added metadata.yml for beginner Blender tutorial
- Enhanced release script functionality
- Added German translations for external link dialog strings
- Implemented external link handling with user preferences and `xdg-open` support
- Added external link click detection and logging in the WebEngine view
- Persisted the current URL when changing view modes in the TutorView
- Added a Dockerfile for an XFCE desktop environment
- Added context menu support for the web view in free mode
- Enabled native window decorations in free floating mode
- Implemented flexible Tutor View with dynamic orientation and mode handling

## Fixes

- Improved JavaScript message handling and URL change detection
- Resolved a reference error by dynamically loading the QWebChannel library
- Implemented web channel message handling for hash state changes
- Improved JavaScript message handling and URL change detection

## Other Changes

- Refactored UnitScanner to use config for scanning unit paths
- Moved LiaScript configuration from hardcoded constants to PortalConfig
- Added LiaScript URL generation and ProgramLaunchInfo to UnitMetadata
- Refactored translation handling for multiple packages
- Removed unused imports and simplify page load handling
- Enhanced JavaScript message handling with detailed logging and error handling
- Fixed DE build pipeline
