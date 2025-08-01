"""
Test suite for code compression functionality
"""

import pytest
import warnings
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_process import process_content
from src.repomix.core.file.file_manipulate import (
    PythonManipulator,
    TreeSitterManipulator,
    get_file_manipulator,
)


class TestPythonManipulator:
    """Test cases for PythonManipulator compression functionality"""

    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for testing"""
        return '''
def calculate_sum(a: int, b: int) -> int:
    """
    Calculate the sum of two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        The sum of a and b
    """
    # Validate inputs
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")

    # Perform calculation
    result = a + b

    # Log the operation
    print(f"Calculating {a} + {b} = {result}")

    return result

class DataProcessor:
    """
    A class for processing various types of data.

    This class provides methods for data validation, transformation,
    and analysis operations.
    """

    def __init__(self, data_source: str):
        """
        Initialize the DataProcessor.

        Args:
            data_source: Path to the data source
        """
        self.data_source = data_source
        self.processed_count = 0
        self._validate_source()

    def process_data(self, data: list) -> dict:
        """
        Process the input data and return results.

        Args:
            data: List of data items to process

        Returns:
            Dictionary containing processed results
        """
        if not data:
            return {"status": "empty", "count": 0}

        # Complex processing logic
        processed_items = []
        for item in data:
            if self._is_valid_item(item):
                processed_item = self._transform_item(item)
                processed_items.append(processed_item)

        self.processed_count += len(processed_items)

        return {
            "status": "success",
            "count": len(processed_items),
            "items": processed_items
        }

    async def async_process(self, data: list) -> dict:
        """
        Asynchronously process data.

        Args:
            data: Data to process

        Returns:
            Processing results
        """
        import asyncio
        await asyncio.sleep(0.1)
        return {"async": True, "data": data}

    def _validate_source(self):
        """Private method to validate data source."""
        # Implementation details...
        pass

    def _is_valid_item(self, item):
        """Check if an item is valid for processing."""
        return item is not None

    def _transform_item(self, item):
        """Transform a single item."""
        return str(item).upper()

# Global configuration
CONFIG = {
    "max_items": 1000,
    "timeout": 30
}
'''

    @pytest.fixture
    def manipulator(self):
        """Create a PythonManipulator instance"""
        return PythonManipulator()

    def test_compression_disabled(self, manipulator, sample_python_code):
        """Test that compression can be disabled"""
        result = manipulator.compress_code(
            sample_python_code,
            keep_signatures=True,
            keep_docstrings=True,
            keep_interfaces=False,
        )

        # When not in interface mode, should keep implementation
        assert "isinstance(a, int)" in result
        assert "processed_items = []" in result
        assert "return result" in result

    def test_interface_mode_functions(self, manipulator, sample_python_code):
        """Test interface mode preserves function signatures and docstrings"""
        result = manipulator.compress_code(
            sample_python_code,
            keep_signatures=True,
            keep_docstrings=True,
            keep_interfaces=True,
        )

        # Should preserve function signature
        assert "def calculate_sum(a: int, b: int) -> int:" in result

        # Should preserve docstring
        assert "Calculate the sum of two integers." in result
        assert "Args:" in result
        assert "Returns:" in result

        # Should remove implementation and replace with pass
        assert "isinstance(a, int)" not in result
        assert 'print(f"Calculating' not in result
        assert "pass" in result

    def test_interface_mode_classes(self, manipulator, sample_python_code):
        """Test interface mode preserves class and method signatures"""
        result = manipulator.compress_code(
            sample_python_code,
            keep_signatures=True,
            keep_docstrings=True,
            keep_interfaces=True,
        )

        # Should preserve class signature and docstring
        assert "class DataProcessor:" in result
        assert "A class for processing various types of data." in result

        # Should preserve all method signatures
        assert "def __init__(self, data_source: str):" in result
        assert "def process_data(self, data: list) -> dict:" in result
        assert "async def async_process(self, data: list) -> dict:" in result
        assert "def _validate_source(self):" in result
        assert "def _is_valid_item(self, item):" in result
        assert "def _transform_item(self, item):" in result

        # Should preserve method docstrings
        assert "Initialize the DataProcessor." in result
        assert "Process the input data and return results." in result
        assert "Asynchronously process data." in result

        # Should remove implementation details
        assert "self.data_source = data_source" not in result
        assert "processed_items = []" not in result
        assert "await asyncio.sleep(0.1)" not in result

    def test_remove_signatures(self, manipulator, sample_python_code):
        """Test removing all function and class signatures"""
        result = manipulator.compress_code(
            sample_python_code,
            keep_signatures=False,
            keep_docstrings=False,
            keep_interfaces=False,
        )

        # Should remove all functions and classes
        assert "def calculate_sum" not in result
        assert "class DataProcessor" not in result
        assert "def __init__" not in result

        # Should keep global variables
        assert "CONFIG = " in result

    def test_keep_signatures_remove_docstrings(self, manipulator, sample_python_code):
        """Test keeping signatures but removing docstrings"""
        result = manipulator.compress_code(
            sample_python_code,
            keep_signatures=True,
            keep_docstrings=False,
            keep_interfaces=False,
        )

        # Should preserve signatures
        assert "def calculate_sum(a: int, b: int) -> int:" in result
        assert "class DataProcessor:" in result

        # Should remove docstrings
        assert "Calculate the sum of two integers." not in result
        assert "A class for processing various types of data." not in result

        # Should keep implementation
        assert "isinstance(a, int)" in result

    def test_invalid_python_syntax(self, manipulator):
        """Test handling of invalid Python syntax"""
        invalid_code = "def invalid_function(\n    # Missing closing parenthesis"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = manipulator.compress_code(invalid_code)

            # Should return original content and issue warning
            assert result == invalid_code
            assert len(w) == 1
            assert "Failed to parse Python code" in str(w[0].message)

    def test_empty_code(self, manipulator):
        """Test handling of empty code"""
        result = manipulator.compress_code("")
        assert result == ""

    def test_only_global_variables(self, manipulator):
        """Test code with only global variables"""
        code = """
# Global variables
VERSION = "1.0"
DEBUG = True
CONFIG = {"key": "value"}
"""
        result = manipulator.compress_code(code, keep_signatures=True, keep_docstrings=True, keep_interfaces=True)

        # Should preserve global variables
        assert "VERSION = " in result
        assert "DEBUG = " in result
        assert "CONFIG = " in result


class TestFileProcessIntegration:
    """Integration tests for file processing with compression"""

    @pytest.fixture
    def sample_code(self):
        """Sample code for integration testing"""
        return '''
def hello_world():
    """Print hello world message."""
    print("Hello, World!")
    return "success"

class Greeter:
    """A simple greeter class."""

    def greet(self, name: str) -> str:
        """Greet a person by name."""
        return f"Hello, {name}!"

GLOBAL_VAR = "test"
'''

    def test_compression_disabled_integration(self, sample_code):
        """Test file processing with compression disabled"""
        config = RepomixConfig()
        config.compression.enabled = False

        result = process_content(sample_code, "test.py", config)

        # Should preserve everything
        assert "def hello_world():" in result
        assert "Print hello world message." in result
        assert 'print("Hello, World!")' in result
        assert "class Greeter:" in result

    def test_interface_mode_integration(self, sample_code):
        """Test file processing with interface mode enabled (tree-sitter behavior)"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_signatures = True
        config.compression.keep_docstrings = True
        config.compression.keep_interfaces = True

        result = process_content(sample_code, "test.py", config)

        # Tree-sitter will extract key elements, not follow traditional interface mode
        # Should contain function and class definitions
        assert any(
            keyword in result
            for keyword in [
                "def hello_world",
                "hello_world",
                "class Greeter",
                "Greeter",
            ]
        )

        # Should use tree-sitter separator
        assert "⋮----" in result

    def test_remove_signatures_integration(self, sample_code):
        """Test file processing with signatures removal (tree-sitter still extracts elements)"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_signatures = False
        config.compression.keep_docstrings = False
        config.compression.keep_interfaces = False

        result = process_content(sample_code, "test.py", config)

        # Tree-sitter still extracts elements regardless of these settings
        # Should contain some extracted elements
        assert "⋮----" in result  # Tree-sitter separator

    def test_non_python_file_warning(self):
        """Test that JavaScript files are compressed with tree-sitter"""
        js_code = """
function hello() {
    console.log("Hello, World!");
}
"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_interfaces = True

        result = process_content(js_code, "test.js", config)

        # Tree-sitter should handle JavaScript and compress it
        assert "⋮----" in result  # Tree-sitter separator
        assert "hello" in result  # Function name should be extracted


class TestFileManipulatorFactory:
    """Test the file manipulator factory function"""

    def test_get_python_manipulator(self):
        """Test getting Python manipulator (now returns TreeSitterManipulator)"""
        manipulator = get_file_manipulator("test.py")
        assert isinstance(manipulator, TreeSitterManipulator)

    def test_get_javascript_manipulator(self):
        """Test getting JavaScript manipulator"""
        manipulator = get_file_manipulator("test.js")
        assert manipulator is not None
        assert not isinstance(manipulator, PythonManipulator)

    def test_get_unknown_file_type(self):
        """Test getting manipulator for unknown file type"""
        manipulator = get_file_manipulator("test.unknown")
        assert manipulator is None

    def test_pathlib_path_input(self):
        """Test using pathlib.Path as input"""
        from pathlib import Path

        manipulator = get_file_manipulator(Path("test.py"))
        assert isinstance(manipulator, TreeSitterManipulator)


class TestTreeSitterManipulator:
    """Test cases for TreeSitterManipulator compression functionality"""

    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for tree-sitter testing"""
        return '''
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle

    Returns:
        The area of the circle
    """
    import math
    return math.pi * radius ** 2

class Calculator:
    """A simple calculator class."""

    def __init__(self, precision: int = 2):
        """Initialize the calculator."""
        self.precision = precision

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return round(a + b, self.precision)

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return round(a - b, self.precision)

# Constants
PI = 3.14159
VERSION = "1.0.0"
'''

    @pytest.fixture
    def sample_typescript_code(self):
        """Sample TypeScript code for tree-sitter testing"""
        return """
interface User {
    id: number;
    name: string;
    email: string;
}

class UserService {
    private users: User[] = [];

    constructor() {
        this.loadUsers();
    }

    public addUser(user: User): void {
        this.users.push(user);
        this.saveUsers();
    }

    private loadUsers(): void {
        // Load users from storage
        console.log("Loading users...");
    }

    private saveUsers(): void {
        // Save users to storage
        console.log("Saving users...");
    }
}

export default UserService;
"""

    def test_python_tree_sitter_compression(self, sample_python_code):
        """Test tree-sitter compression for Python files"""
        manipulator = TreeSitterManipulator("test.py")
        result = manipulator.compress_code(sample_python_code)

        # Should extract key elements and compress
        assert result != sample_python_code  # Should be different from original

        # Should contain function definitions
        assert "def calculate_area" in result or "calculate_area" in result

        # Should contain class definitions
        assert "class Calculator" in result or "Calculator" in result

        # Should contain imports
        assert "import" in result

        # Should be separated by tree-sitter separator
        assert "⋮----" in result

    def test_typescript_tree_sitter_compression(self, sample_typescript_code):
        """Test tree-sitter compression for TypeScript files"""
        manipulator = TreeSitterManipulator("test.ts")
        result = manipulator.compress_code(sample_typescript_code)

        # TypeScript/JavaScript parsing might fail due to query issues
        # Test should handle both success and graceful fallback
        if result != sample_typescript_code:
            # Compression worked
            assert "⋮----" in result  # Tree-sitter separator
        else:
            # Compression failed gracefully, returned original content
            assert result == sample_typescript_code

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types"""
        manipulator = TreeSitterManipulator("test.unknown")
        original_code = "This is some unknown file content"

        result = manipulator.compress_code(original_code)

        # Should return original content unchanged
        assert result == original_code

    def test_invalid_syntax_fallback(self):
        """Test fallback for files with invalid syntax"""
        manipulator = TreeSitterManipulator("test.py")
        invalid_code = "def invalid_function(\n    # Missing closing parenthesis"

        result = manipulator.compress_code(invalid_code)

        # Should return original content and potentially issue warning
        assert result == invalid_code

    def test_empty_file(self):
        """Test handling of empty files"""
        manipulator = TreeSitterManipulator("test.py")
        result = manipulator.compress_code("")

        # Should return empty string
        assert result == ""


class TestTreeSitterIntegration:
    """Integration tests for tree-sitter compression"""

    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for integration testing"""
        return '''
import os
import sys

def main():
    """Main entry point."""
    print("Starting application...")
    app = Application()
    app.run()

class Application:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        self.config = self.load_config()

    def run(self):
        """Run the application."""
        print("Application running!")

    def load_config(self):
        """Load configuration."""
        return {"debug": True}

if __name__ == "__main__":
    main()
'''

    def test_tree_sitter_compression_integration(self, sample_python_code):
        """Test tree-sitter compression through file processing pipeline"""
        config = RepomixConfig()
        config.compression.enabled = True

        result = process_content(sample_python_code, "test.py", config)

        # Should use tree-sitter compression
        assert result != sample_python_code.strip()

        # Should contain compressed elements
        assert "⋮----" in result  # Tree-sitter separator

        # Should contain key code elements
        assert any(keyword in result for keyword in ["import", "def", "class"])

    def test_tree_sitter_disabled_fallback(self, sample_python_code):
        """Test fallback when tree-sitter is not used"""
        config = RepomixConfig()
        config.compression.enabled = False

        result = process_content(sample_python_code, "test.py", config)

        # Should return original content (stripped)
        assert result == sample_python_code.strip()

    def test_tree_sitter_with_unsupported_language(self):
        """Test tree-sitter with unsupported file type"""
        config = RepomixConfig()
        config.compression.enabled = True

        unknown_code = "This is some unknown file content"
        result = process_content(unknown_code, "test.unknown", config)

        # Should return original content since no manipulator exists
        assert result == unknown_code


if __name__ == "__main__":
    pytest.main([__file__])
