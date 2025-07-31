"""Language loading utilities for tree-sitter parsers."""

import importlib
from typing import Dict, Optional
from tree_sitter import Language, Parser


class LanguageLoader:
    """Handles loading and caching of tree-sitter languages."""
    
    _instance: Optional['LanguageLoader'] = None
    _languages: Dict[str, Language] = {}
    
    def __new__(cls) -> 'LanguageLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_language(self, language_name: str) -> Optional[Language]:
        """Get a tree-sitter language by name.
        
        Args:
            language_name: Name of the language (e.g., 'python', 'javascript')
            
        Returns:
            Language object if available, None otherwise
        """
        if language_name in self._languages:
            return self._languages[language_name]
        
        try:
            # Try to import the specific language package
            if language_name == 'python':
                import tree_sitter_python as tsp
                language = Language(tsp.language())
            elif language_name == 'javascript':
                import tree_sitter_javascript as tsjs
                language = Language(tsjs.language())
            elif language_name == 'typescript':
                # TypeScript uses JavaScript parser
                import tree_sitter_javascript as tsjs
                language = Language(tsjs.language())
            else:
                # Try generic import pattern
                module_name = f'tree_sitter_{language_name}'
                module = importlib.import_module(module_name)
                language = Language(module.language())
            
            self._languages[language_name] = language
            return language
            
        except ImportError:
            # Language package not available
            return None
        except Exception:
            # Other errors loading language
            return None
    
    def create_parser(self, language_name: str) -> Optional[Parser]:
        """Create a parser for the given language.
        
        Args:
            language_name: Name of the language
            
        Returns:
            Parser instance if language is available, None otherwise
        """
        language = self.get_language(language_name)
        if language is None:
            return None
        
        parser = Parser(language)
        return parser
    
    def is_language_available(self, language_name: str) -> bool:
        """Check if a language is available.
        
        Args:
            language_name: Name of the language
            
        Returns:
            True if language is available, False otherwise
        """
        return self.get_language(language_name) is not None


# Global instance
language_loader = LanguageLoader()