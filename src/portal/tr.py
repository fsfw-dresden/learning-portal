from core.translation import get_translation_manager

# Register the portal module with the translation manager
get_translation_manager().register_module("portal", "Portal")

def tr(text: str) -> str:
    """Helper function for translations"""
    return get_translation_manager().tr(text, "portal")