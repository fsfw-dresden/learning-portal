import os
import logging
from typing import Dict, Optional, List
from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtWidgets import QApplication

class TranslationManager:
    """
    A singleton manager for handling translations across multiple modules.
    
    This class provides a centralized way to manage translations for different modules,
    allowing them to be loaded on-demand when modules are used by other applications.
    """
    _instance = None
    
    def __init__(self):
        self.translators: Dict[str, QTranslator] = {}
        self.contexts: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def get_instance(cls) -> 'TranslationManager':
        """Get the singleton instance of the TranslationManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_module(self, module_name: str, context: str = None) -> None:
        """
        Register a module with the translation manager
        
        Args:
            module_name: The name of the module (e.g., 'portal', 'tutor')
            context: The translation context to use for this module.
                     If None, the capitalized module name will be used.
        """
        if context is None:
            context = module_name.capitalize()
        self.contexts[module_name] = context
        self.logger.debug(f"Registered module '{module_name}' with context '{context}'")
        
    def load_translations(self, module_name: str) -> bool:
        """
        Load translations for a specific module
        
        Args:
            module_name: The name of the module to load translations for
            
        Returns:
            True if translations were loaded successfully, False otherwise
        """
        if module_name in self.translators:
            self.logger.debug(f"Translations for '{module_name}' already loaded")
            return True  # Already loaded
            
        translator = QTranslator()
        locale = QLocale()
        
        try:
            import pkg_resources
            translations_dir = pkg_resources.resource_filename(module_name, 'translations')
        except (ImportError, pkg_resources.DistributionNotFound):
            translations_dir = os.path.join(os.path.dirname(__file__), "..", module_name, "translations")
        
        # Try loading translations in order of preference
        if (translator.load(locale, module_name, "_", translations_dir) or
            translator.load(QLocale(locale.language()), module_name, "_", translations_dir) or
            (locale.language() != QLocale.English and translator.load(f"{module_name}_en", translations_dir))):
            
            QApplication.instance().installTranslator(translator)
            self.translators[module_name] = translator
            self.logger.info(f"Loaded translations for module: {module_name}")
            return True
        
        self.logger.warning(f"No translations found for module: {module_name}")
        return False
    
    def unload_translations(self, module_name: str) -> bool:
        """
        Unload translations for a specific module
        
        Args:
            module_name: The name of the module to unload translations for
            
        Returns:
            True if translations were unloaded successfully, False otherwise
        """
        if module_name not in self.translators:
            self.logger.debug(f"No translations loaded for '{module_name}'")
            return False
            
        translator = self.translators.pop(module_name)
        QApplication.instance().removeTranslator(translator)
        self.logger.info(f"Unloaded translations for module: {module_name}")
        return True
    
    def tr(self, text: str, module_name: str, *args) -> str:
        """
        Translate text using the specified module's context
        
        Args:
            text: The text to translate
            module_name: The name of the module to use for translation context
            *args: Optional arguments for string formatting
            
        Returns:
            The translated text
        """
        if module_name not in self.contexts:
            self.logger.warning(f"Module '{module_name}' not registered for translation")
            return text
            
        context = self.contexts[module_name]
        translated = QApplication.translate(context, text)
        
        if args:
            return translated % args
        return translated

# Convenience functions

def get_translation_manager() -> TranslationManager:
    """Get the singleton instance of the TranslationManager"""
    return TranslationManager.get_instance()

def tr(text: str, module_name: str, *args) -> str:
    """
    Translate text using the specified module's context
    
    Args:
        text: The text to translate
        module_name: The name of the module to use for translation context
        *args: Optional arguments for string formatting
        
    Returns:
        The translated text
    """
    return get_translation_manager().tr(text, module_name, *args)

def load_module_translations(module_name: str) -> bool:
    """
    Load translations for a specific module
    
    Args:
        module_name: The name of the module to load translations for
        
    Returns:
        True if translations were loaded successfully, False otherwise
    """
    return get_translation_manager().load_translations(module_name)

def unload_module_translations(module_name: str) -> bool:
    """
    Unload translations for a specific module
    
    Args:
        module_name: The name of the module to unload translations for
        
    Returns:
        True if translations were unloaded successfully, False otherwise
    """
    return get_translation_manager().unload_translations(module_name)

def register_module(module_name: str, context: str = None) -> None:
    """
    Register a module with the translation manager
    
    Args:
        module_name: The name of the module (e.g., 'portal', 'tutor')
        context: The translation context to use for this module.
                 If None, the capitalized module name will be used.
    """
    get_translation_manager().register_module(module_name, context)