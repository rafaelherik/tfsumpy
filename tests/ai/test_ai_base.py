import pytest
from unittest.mock import Mock, patch, AsyncMock
from tfsumpy.ai.base import AIBase
from tfsumpy.models import ResourceChange

@pytest.fixture
def sample_resources():
    return [
        {
            'action': 'create',
            'resource_type': 'aws_instance',
            'identifier': 'test-instance',
            'before': {},
            'after': {'name': 'test', 'type': 't2.micro'}
        },
        {
            'action': 'update',
            'resource_type': 'aws_security_group',
            'identifier': 'test-sg',
            'before': {'name': 'old-sg'},
            'after': {'name': 'new-sg'}
        }
    ]

@pytest.fixture
def ai_base():
    return AIBase()

def test_convert_to_resource_changes(ai_base, sample_resources):
    """Test conversion of resource dictionaries to ResourceChange objects."""
    changes = ai_base._convert_to_resource_changes(sample_resources)
    
    assert len(changes) == 2
    assert isinstance(changes[0], ResourceChange)
    assert changes[0].action == 'create'
    assert changes[0].resource_type == 'aws_instance'
    assert changes[0].identifier == 'test-instance'
    assert changes[0].data['after'] == {'name': 'test', 'type': 't2.micro'}

def test_get_ai_summary_no_config(ai_base, sample_resources):
    """Test get_ai_summary with no AI config."""
    data = {'resources': sample_resources}
    summary = ai_base.get_ai_summary(data)
    assert summary is None

def test_get_ai_summary_no_resources(ai_base):
    """Test get_ai_summary with no resources."""
    data = {}
    ai_config = {'provider': 'openai', 'api_key': 'test-key'}
    summary = ai_base.get_ai_summary(data, ai_config)
    assert summary is None

@patch('tfsumpy.ai.base.create_summarizer')
def test_get_ai_summary_success(mock_create_summarizer, ai_base, sample_resources):
    """Test successful AI summary generation."""
    # Mock the summarizer with an async mock
    mock_summarizer = AsyncMock()
    mock_summarizer.summarize.return_value = "Test summary"
    mock_create_summarizer.return_value = mock_summarizer
    
    data = {'resources': sample_resources}
    ai_config = {'provider': 'openai', 'api_key': 'test-key'}
    
    summary = ai_base.get_ai_summary(data, ai_config)
    
    assert summary == "Test summary"
    mock_create_summarizer.assert_called_once()
    mock_summarizer.summarize.assert_called_once()

@patch('tfsumpy.ai.base.create_summarizer')
def test_get_ai_summary_error(mock_create_summarizer, ai_base, sample_resources):
    """Test error handling in AI summary generation."""
    # Mock the summarizer to raise an exception
    mock_create_summarizer.side_effect = Exception("Test error")
    
    data = {'resources': sample_resources}
    ai_config = {'provider': 'openai', 'api_key': 'test-key'}
    
    summary = ai_base.get_ai_summary(data, ai_config)
    
    assert summary is None
    mock_create_summarizer.assert_called_once() 