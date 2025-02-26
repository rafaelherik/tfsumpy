import pytest
import json
import tempfile
from unittest.mock import Mock, patch
from bolwerk.context import Context
from bolwerk.analyzer import AnalyzerInterface, AnalyzerResult
from bolwerk.reporter import ReporterInterface

@pytest.fixture
def mock_analyzer():
    """Fixture for creating a mock analyzer."""
    analyzer = Mock(spec=AnalyzerInterface)
    analyzer.category = "test_category"
    analyzer.analyze.return_value = AnalyzerResult(category="test_category", data=[])
    return analyzer

@pytest.fixture
def mock_reporter():
    """Fixture for creating a mock reporter."""
    reporter = Mock(spec=ReporterInterface)
    reporter.category = "test_category"
    return reporter

@pytest.fixture
def sample_config():
    """Fixture for creating a sample configuration."""
    return {
        "sensitive_patterns": [
            {"pattern": "test_pattern", "replacement": "***"},
            {"pattern": "password", "replacement": "###"}
        ],
        "risk_rules": {
            "high": [{"pattern": "test_rule", "message": "test message"}],
            "medium": [{"pattern": "medium_rule", "message": "medium message"}]
        }
    }

@pytest.fixture
def config_file(sample_config):
    """Fixture for creating a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f)
        return f.name

def test_context_initialization():
    """Test Context initialization with different parameters."""
    # Test default initialization
    context = Context()
    assert context.debug is False
    assert context.config_path is None
    assert isinstance(context.sensitive_patterns, list)
    assert isinstance(context._analyzers, dict)
    assert isinstance(context._reporters, dict)

    # Test debug mode
    context_debug = Context(debug=True)
    assert context_debug.debug is True

    # Test with config path
    context_with_config = Context(config_path="test_path")
    assert context_with_config.config_path == "test_path"

def test_analyzer_registration(mock_analyzer):
    """Test analyzer registration functionality."""
    context = Context()
    
    # Test successful registration
    context.register_analyzer(mock_analyzer)
    assert mock_analyzer in context.get_analyzers("test_category")
    
    # Test duplicate registration
    context.register_analyzer(mock_analyzer)
    assert len(context.get_analyzers("test_category")) == 1
    
    # Test invalid analyzer
    with pytest.raises(ValueError):
        context.register_analyzer(Mock())

def test_reporter_registration(mock_reporter):
    """Test reporter registration functionality."""
    context = Context()
    
    # Test successful registration
    context.register_reporter(mock_reporter)
    assert mock_reporter in context.get_reporters("test_category")
    
    # Test duplicate registration
    context.register_reporter(mock_reporter)
    assert len(context.get_reporters("test_category")) == 1
    
    # Test invalid reporter
    with pytest.raises(ValueError):
        context.register_reporter(Mock())

def test_run_analyzers(mock_analyzer):
    """Test analyzer execution functionality."""
    context = Context()
    context.register_analyzer(mock_analyzer)
    
    # Test successful execution
    results = context.run_analyzers("test_category")
    assert len(results) == 1
    mock_analyzer.analyze.assert_called_once()
    
    # Test execution with no analyzers
    results = context.run_analyzers("non_existent_category")
    assert len(results) == 0
    
    # Test execution with failing analyzer
    mock_analyzer.analyze.side_effect = Exception("Test error")
    results = context.run_analyzers("test_category")
    assert len(results) == 0

def test_run_reporters(mock_reporter):
    """Test reporter execution functionality."""
    context = Context()
    context.register_reporter(mock_reporter)
    
    # Test successful execution
    context.run_reports("test_category", data={"test": "data"})
    mock_reporter.print_report.assert_called_once()
    
    # Test execution with no reporters
    context.run_reports("non_existent_category", data={})
    
    # Test execution with failing reporter
    mock_reporter.print_report.side_effect = Exception("Test error")
    context.run_reports("test_category", data={})

def test_plan_data_management():
    """Test plan data storage and retrieval."""
    context = Context()
    test_data = {"resource": "test_resource"}
    
    # Test setting and getting plan data
    context.set_plan_data(test_data)
    assert context.get_plan_data() == test_data
    
    # Test overwriting plan data
    new_data = {"resource": "new_resource"}
    context.set_plan_data(new_data)
    assert context.get_plan_data() == new_data

@patch('builtins.open')
def test_load_config_file_not_found(mock_open):
    """Test configuration loading with missing file."""
    mock_open.side_effect = FileNotFoundError
    context = Context()
    
    with pytest.raises(FileNotFoundError):
        context.load_config()

def test_load_config_with_external(config_file, sample_config):
    """Test configuration loading and merging with external config."""
    context = Context(config_path=config_file)
    context.load_config()
    
    # Verify sensitive patterns are loaded
    assert len(context.sensitive_patterns) > 0
    assert any(pattern[0] == "test_pattern" for pattern in context.sensitive_patterns)
    assert any(pattern[0] == "password" for pattern in context.sensitive_patterns)

@patch('json.load')
def test_load_config_invalid_json(mock_json_load):
    """Test configuration loading with invalid JSON."""
    mock_json_load.side_effect = json.JSONDecodeError("Test error", "", 0)
    context = Context()
    
    with pytest.raises(json.JSONDecodeError):
        context.load_config() 