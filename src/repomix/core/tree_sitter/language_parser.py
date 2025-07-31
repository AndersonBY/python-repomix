"""Main language parser manager for tree-sitter integration."""

import logging
import tree_sitter
from typing import Dict, Optional
from tree_sitter import Parser, Query

from .load_language import language_loader
from .lang2query import get_query_module_name
from .parse_strategies.parse_strategy import ParseStrategy, ParseStrategyFactory


logger = logging.getLogger(__name__)


class LanguageParser:
    """Singleton class managing parsers, queries, and strategies for each language."""
    
    _instance: Optional['LanguageParser'] = None
    _parsers: Dict[str, Parser] = {}
    _queries: Dict[str, Query] = {}
    _strategies: Dict[str, ParseStrategy] = {}
    
    def __new__(cls) -> 'LanguageParser':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_parser(self, language: str) -> Optional[Parser]:
        """Get or create a parser for the given language.
        
        Args:
            language: Language name (e.g., 'python', 'javascript')
            
        Returns:
            Parser instance if available, None otherwise
        """
        if language in self._parsers:
            return self._parsers[language]
        
        parser = language_loader.create_parser(language)
        if parser is not None:
            self._parsers[language] = parser
        
        return parser
    
    def get_query(self, language: str) -> Optional[Query]:
        """Get or create a query for the given language.
        
        Args:
            language: Language name
            
        Returns:
            Query instance if available, None otherwise
        """
        if language in self._queries:
            return self._queries[language]
        
        query_module_name = get_query_module_name(language)
        if query_module_name is None:
            return None
        
        try:
            # Import the query module dynamically
            module = __import__(f'repomix.core.tree_sitter.queries.{query_module_name}', 
                              fromlist=[query_module_name])
            
            # Get the query string from the module
            query_attr_name = f'query_{language}'
            if hasattr(module, query_attr_name):
                query_string = getattr(module, query_attr_name)
            else:
                # Try alternative naming
                query_string = getattr(module, 'query', None)
            
            if query_string is None:
                logger.warning(f"No query string found in {query_module_name}")
                return None
            
            # Get the language to create the query
            tree_sitter_language = language_loader.get_language(language)
            if tree_sitter_language is None:
                return None
            
            query = tree_sitter.Query(tree_sitter_language, query_string)
            self._queries[language] = query
            return query
            
        except ImportError:
            logger.warning(f"Query module {query_module_name} not found")
            return None
        except Exception as e:
            logger.error(f"Error loading query for {language}: {e}")
            return None
    
    def get_strategy(self, language: str) -> ParseStrategy:
        """Get or create a parse strategy for the given language.
        
        Args:
            language: Language name
            
        Returns:
            ParseStrategy instance (default strategy if specific one not available)
        """
        if language in self._strategies:
            return self._strategies[language]
        
        strategy = ParseStrategyFactory.create_strategy(language)
        self._strategies[language] = strategy
        return strategy
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported.
        
        Args:
            language: Language name
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_loader.is_language_available(language)
    
    def clear_cache(self) -> None:
        """Clear all cached parsers, queries, and strategies."""
        self._parsers.clear()
        self._queries.clear()
        self._strategies.clear()


# Global instance
language_parser = LanguageParser()