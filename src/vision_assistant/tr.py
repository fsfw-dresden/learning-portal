from core.translation import get_translation_manager

# Translation context for vision assistant
TRANSLATION_CONTEXT = "VisionAssistant"

# Register the vision_assistant module with the translation manager
get_translation_manager().register_module("vision_assistant", TRANSLATION_CONTEXT)

def tr(text: str, *args) -> str:
    """Helper function for translations with variable substitution"""
    return get_translation_manager().tr(text, "vision_assistant", *args)