from core.translation import get_translation_manager

# Translation context for all welcome wizard pages
TRANSLATION_CONTEXT = "WelcomeWizard"

# Register the welcome module with the translation manager
get_translation_manager().register_module("welcome", TRANSLATION_CONTEXT)

def tr(text: str, *args) -> str:
    """Helper function for translations with variable substitution"""
    return get_translation_manager().tr(text, "welcome", *args)