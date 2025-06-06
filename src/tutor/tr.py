from core.translation import get_translation_manager

# Translation context for all tutor pages
TRANSLATION_CONTEXT = "TutorView"

# Register the tutor module with the translation manager
get_translation_manager().register_module("tutor", TRANSLATION_CONTEXT)

def tr(text: str, *args) -> str:
    """Helper function for translations with variable substitution"""
    return get_translation_manager().tr(text, "tutor", *args)