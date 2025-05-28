"""
Test suite for code compression functionality
"""

import pytest
import warnings
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_process import process_content
from src.repomix.core.file.file_manipulate import PythonManipulator, get_file_manipulator


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
        result = manipulator.compress_code(sample_python_code, keep_signatures=True, keep_docstrings=True, keep_interfaces=False)

        # When not in interface mode, should keep implementation
        assert "isinstance(a, int)" in result
        assert "processed_items = []" in result
        assert "return result" in result

    def test_interface_mode_functions(self, manipulator, sample_python_code):
        """Test interface mode preserves function signatures and docstrings"""
        result = manipulator.compress_code(sample_python_code, keep_signatures=True, keep_docstrings=True, keep_interfaces=True)

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
        result = manipulator.compress_code(sample_python_code, keep_signatures=True, keep_docstrings=True, keep_interfaces=True)

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
        result = manipulator.compress_code(sample_python_code, keep_signatures=False, keep_docstrings=False, keep_interfaces=False)

        # Should remove all functions and classes
        assert "def calculate_sum" not in result
        assert "class DataProcessor" not in result
        assert "def __init__" not in result

        # Should keep global variables
        assert "CONFIG = " in result

    def test_keep_signatures_remove_docstrings(self, manipulator, sample_python_code):
        """Test keeping signatures but removing docstrings"""
        result = manipulator.compress_code(sample_python_code, keep_signatures=True, keep_docstrings=False, keep_interfaces=False)

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
        """Test file processing with interface mode enabled"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_signatures = True
        config.compression.keep_docstrings = True
        config.compression.keep_interfaces = True

        result = process_content(sample_code, "test.py", config)

        # Should preserve signatures and docstrings
        assert "def hello_world():" in result
        assert "Print hello world message." in result
        assert "def greet(self, name: str) -> str:" in result
        assert "Greet a person by name." in result

        # Should remove implementation
        assert 'print("Hello, World!")' not in result
        assert 'return f"Hello, {name}!"' not in result

        # Should have pass statements
        assert "pass" in result

    def test_remove_signatures_integration(self, sample_code):
        """Test file processing with signatures removal"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_signatures = False
        config.compression.keep_docstrings = False
        config.compression.keep_interfaces = False

        result = process_content(sample_code, "test.py", config)

        # Should remove all functions and classes
        assert "def hello_world" not in result
        assert "class Greeter" not in result

        # Should keep global variables
        assert "GLOBAL_VAR = " in result

    def test_non_python_file_warning(self):
        """Test that non-Python files show appropriate warnings"""
        js_code = """
function hello() {
    console.log("Hello, World!");
}
"""
        config = RepomixConfig()
        config.compression.enabled = True
        config.compression.keep_interfaces = True

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = process_content(js_code, "test.js", config)

            # Should return original content and issue warning
            assert result.strip() == js_code.strip()
            assert len(w) == 1
            assert "Code compression not implemented" in str(w[0].message)


class TestFileManipulatorFactory:
    """Test the file manipulator factory function"""

    def test_get_python_manipulator(self):
        """Test getting Python manipulator"""
        manipulator = get_file_manipulator("test.py")
        assert isinstance(manipulator, PythonManipulator)

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
        assert isinstance(manipulator, PythonManipulator)


if __name__ == "__main__":
    pytest.main([__file__])
