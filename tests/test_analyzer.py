import pytest
import dataclasses
from tfsumpy.analyzer import (
    AnalyzerCategory,
    AnalyzerResult,
    AnalyzerInterface
)

def test_analyzer_category():
    """Test AnalyzerCategory enum."""
    # Test enum values
    assert AnalyzerCategory.PLAN.name == "PLAN"
    assert AnalyzerCategory.SECURITY.name == "SECURITY"
    assert AnalyzerCategory.COST.name == "COST"
    assert AnalyzerCategory.COMPLIANCE.name == "COMPLIANCE"
    
    # Test enum comparison
    assert AnalyzerCategory.PLAN != AnalyzerCategory.SECURITY
    assert AnalyzerCategory.PLAN == AnalyzerCategory.PLAN

def test_analyzer_result():
    """Test AnalyzerResult dataclass."""
    # Test default values
    result = AnalyzerResult(
        category=AnalyzerCategory.PLAN,
        data={"test": "data"}
    )
    assert result.category == AnalyzerCategory.PLAN
    assert result.data == {"test": "data"}
    assert result.success is True
    assert result.error == ""
    
    # Test with error
    result = AnalyzerResult(
        category=AnalyzerCategory.PLAN,
        data=None,
        success=False,
        error="Test error"
    )
    assert result.success is False
    assert result.error == "Test error"
    
    # Test with different data types
    result = AnalyzerResult(
        category=AnalyzerCategory.PLAN,
        data=[1, 2, 3]
    )
    assert result.data == [1, 2, 3]
    
    result = AnalyzerResult(
        category=AnalyzerCategory.PLAN,
        data="string data"
    )
    assert result.data == "string data"

@pytest.fixture
def test_analyzer():
    """Fixture providing a test analyzer implementation."""
    class TestAnalyzer(AnalyzerInterface):
        @property
        def category(self) -> AnalyzerCategory:
            return AnalyzerCategory.PLAN
        
        def analyze(self, context, **kwargs) -> AnalyzerResult:
            return AnalyzerResult(
                category=self.category,
                data={"test": "data"}
            )
    return TestAnalyzer()

def test_analyzer_interface(test_analyzer):
    """Test AnalyzerInterface implementation."""
    # Test category property
    assert test_analyzer.category == AnalyzerCategory.PLAN
    
    # Test analyze method
    result = test_analyzer.analyze(None)
    assert isinstance(result, AnalyzerResult)
    assert result.category == AnalyzerCategory.PLAN
    assert result.data == {"test": "data"}
    assert result.success is True

def test_analyzer_interface_protocol(test_analyzer):
    """Test AnalyzerInterface protocol compliance."""
    # Test valid implementation
    assert isinstance(test_analyzer, AnalyzerInterface)
    
    # Test invalid implementation
    class InvalidAnalyzer:
        pass
    
    assert not isinstance(InvalidAnalyzer(), AnalyzerInterface)
    
    # Test partial implementation
    class PartialAnalyzer:
        @property
        def category(self) -> AnalyzerCategory:
            return AnalyzerCategory.PLAN
    
    assert not isinstance(PartialAnalyzer(), AnalyzerInterface)

def test_analyzer_result_immutability():
    """Test AnalyzerResult immutability."""
    result = AnalyzerResult(
        category=AnalyzerCategory.PLAN,
        data={"test": "data"}
    )
    
    # Test that attributes can't be modified
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.category = AnalyzerCategory.SECURITY
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.data = {"new": "data"}
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.success = False
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.error = "New error" 