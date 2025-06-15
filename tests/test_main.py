import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tfsumpy.__main__ import (
    validate_plan_file,
    get_ai_config,
    main,
    TFSumpyError,
    ConfigurationError,
    ValidationError
)

@pytest.fixture
def mock_plan_file(tmp_path):
    """Create a temporary plan file for testing."""
    plan_file = tmp_path / "test.tfplan"
    plan_file.write_text("test plan content")
    return str(plan_file)

@pytest.fixture
def mock_config_file(tmp_path):
    """Create a temporary config file for testing."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"sensitive_patterns": []}')
    return str(config_file)

def test_validate_plan_file(mock_plan_file):
    """Test plan file validation."""
    # Test valid file
    validate_plan_file(mock_plan_file)
    
    # Test non-existent file
    with pytest.raises(ValidationError):
        validate_plan_file("non_existent.tfplan")
    
    # Test directory instead of file
    with pytest.raises(ValidationError):
        validate_plan_file(str(Path(mock_plan_file).parent))
    
    # Test unreadable file
    os.chmod(mock_plan_file, 0o000)
    with pytest.raises(ValidationError):
        validate_plan_file(mock_plan_file)
    os.chmod(mock_plan_file, 0o644)  # Restore permissions

def test_get_ai_config():
    """Test AI configuration handling."""
    # Test no AI config
    args = Mock(ai=None)
    assert get_ai_config(args) is None
    
    # Test missing API key
    args = Mock(ai=["openai"])
    with pytest.raises(ValidationError):
        get_ai_config(args)
    
    # Test invalid provider
    args = Mock(ai=["invalid", "key"])
    with pytest.raises(ValidationError):
        get_ai_config(args)
    
    # Test valid config with command line API key
    args = Mock(
        ai=["openai", "test_key"],
        ai_model=None,
        ai_max_tokens=1000,
        ai_temperature=0.7,
        ai_system_prompt=None
    )
    config = get_ai_config(args)
    assert config["provider"] == "openai"
    assert config["api_key"] == "test_key"
    assert config["model"] == "gpt-3.5-turbo"
    
    # Test valid config with environment variable API key
    with patch.dict(os.environ, {"TFSUMPY_OPENAI_API_KEY": "env_key"}):
        args = Mock(ai=["openai", "cmd_key"])
        config = get_ai_config(args)
        assert config["api_key"] == "env_key"

@patch('tfsumpy.__main__.Context')
@patch('tfsumpy.__main__.PlanAnalyzer')
@patch('tfsumpy.__main__.PlanReporter')
@patch('tfsumpy.__main__.load_plugins')
def test_main_success(mock_load_plugins, mock_plan_reporter, mock_plan_analyzer, mock_context, mock_plan_file):
    """Test successful main execution."""
    # Setup mocks
    mock_context_instance = Mock()
    mock_context.return_value = mock_context_instance
    mock_plan_analyzer_instance = Mock()
    mock_plan_analyzer.return_value = mock_plan_analyzer_instance
    mock_plan_reporter_instance = Mock()
    mock_plan_reporter.return_value = mock_plan_reporter_instance
    
    # Mock analyzer results
    mock_result = Mock()
    mock_result.data = {"total_changes": 0}
    mock_context_instance.run_analyzers.return_value = [mock_result]
    
    # Test with default output
    with patch('sys.argv', ['tfsumpy', mock_plan_file]), \
         patch('sys.exit') as mock_exit:
        main()
        mock_context_instance.register_analyzer.assert_called_once()
        mock_context_instance.register_reporter.assert_called_once()
        mock_context_instance.run_analyzers.assert_called_once()
        mock_exit.assert_not_called()
    
    # Test with markdown output
    with patch('sys.argv', ['tfsumpy', mock_plan_file, '--output', 'markdown']), \
         patch('sys.exit') as mock_exit:
        main()
        mock_plan_reporter_instance.print_report_markdown.assert_called_once()
        mock_exit.assert_not_called()
    
    # Test with JSON output
    with patch('sys.argv', ['tfsumpy', mock_plan_file, '--output', 'json']), \
         patch('sys.exit') as mock_exit:
        main()
        mock_plan_reporter_instance.print_report_json.assert_called_once()
        mock_exit.assert_not_called()

@patch('tfsumpy.__main__.Context')
def test_main_error_handling(mock_context, mock_plan_file):
    """Test error handling in main function."""
    # Test validation error
    with patch('sys.argv', ['tfsumpy', 'non_existent.tfplan']), \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    
    # Test configuration error
    mock_context.side_effect = ConfigurationError("Test error")
    with patch('sys.argv', ['tfsumpy', mock_plan_file]), \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    
    # Test unexpected error
    mock_context.side_effect = Exception("Unexpected error")
    with patch('sys.argv', ['tfsumpy', mock_plan_file]), \
         pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

def test_deprecated_arguments(mock_plan_file):
    """Test handling of deprecated arguments."""
    # Setup mock result
    mock_result = Mock()
    mock_result.data = {
        "total_changes": 0,
        "change_breakdown": {
            "create": 0,
            "update": 0,
            "delete": 0
        }
    }
    
    # Test --changes deprecation
    with patch('sys.argv', ['tfsumpy', mock_plan_file, '--changes']), \
         patch('warnings.warn') as mock_warn, \
         patch('tfsumpy.__main__.Context') as mock_context, \
         patch('sys.exit') as mock_exit:
        mock_context_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.run_analyzers.return_value = [mock_result]
        main()
        mock_warn.assert_called()
        mock_exit.assert_not_called()
    
    # Test --details deprecation
    with patch('sys.argv', ['tfsumpy', mock_plan_file, '--details']), \
         patch('warnings.warn') as mock_warn, \
         patch('tfsumpy.__main__.Context') as mock_context, \
         patch('sys.exit') as mock_exit:
        mock_context_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.run_analyzers.return_value = [mock_result]
        main()
        mock_warn.assert_called()
        mock_exit.assert_not_called()
    
    # Test --markdown deprecation
    with patch('sys.argv', ['tfsumpy', mock_plan_file, '--markdown']), \
         patch('warnings.warn') as mock_warn, \
         patch('tfsumpy.__main__.Context') as mock_context, \
         patch('sys.exit') as mock_exit:
        mock_context_instance = Mock()
        mock_context.return_value = mock_context_instance
        mock_context_instance.run_analyzers.return_value = [mock_result]
        main()
        mock_warn.assert_called()
        mock_exit.assert_not_called() 