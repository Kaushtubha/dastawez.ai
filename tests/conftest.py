import sys
import types
from pathlib import Path

# Automatically ensure project root is on sys.path for all test runners
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Zero-dependency fallback shim if pytest is not installed in the environment
try:
    import pytest
except ImportError:
    pytest_shim = types.ModuleType("pytest")

    class _RaisesContext:
        def __init__(self, expected_exception):
            self.expected = expected_exception
            self.value = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"Expected exception {self.expected} was not raised.")
            self.value = exc_val
            return issubclass(exc_type, self.expected)

    def _raises(expected_exception):
        return _RaisesContext(expected_exception)

    def _skip(reason=""):
        pass

    def _fixture(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

    pytest_shim.raises = _raises
    pytest_shim.skip = _skip
    pytest_shim.fixture = _fixture
    sys.modules["pytest"] = pytest_shim
