from typing import Dict, Any, List, Optional
from ..reporters.base_reporter import BaseReporter
from ..reporter import ReporterInterface
from .summarizer import SummarizerConfig, create_summarizer
from ..models import ResourceChange
import asyncio
import logging

class AIPlanReporter(BaseReporter, ReporterInterface):
    """Handles AI-based summarization of Terraform plan results."""
    
    def __init__(self):
        """Initialize the AI plan reporter."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._ai_summarizer = None

    @property
    def category(self) -> str:
        return "plan"

    def _get_ai_summarizer(self, config: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get or create AI summarizer instance."""
        if not config:
            return None
            
        if not self._ai_summarizer:
            ai_config = SummarizerConfig(
                provider=config.get('provider', 'openai'),
                model=config.get('model', 'gpt-3.5-turbo'),
                api_key=config.get('api_key'),
                max_tokens=config.get('max_tokens', 10000),
                temperature=config.get('temperature', 0.7),
                system_prompt=config.get('system_prompt')
            )
            self._ai_summarizer = create_summarizer(ai_config)
        
        return self._ai_summarizer

    def _convert_to_resource_changes(self, resources: List[Dict[str, Any]]) -> List[ResourceChange]:
        """Convert resource dictionaries to ResourceChange objects."""
        resource_changes = []
        for resource in resources:
            change = ResourceChange(
                action=resource['action'],
                resource_type=resource['resource_type'],
                identifier=resource['identifier'],
                data={
                    'changes': resource.get('changes', {}),
                    'before': resource.get('before', {}),
                    'after': resource.get('after', {})
                }
            )
            resource_changes.append(change)
        return resource_changes

    def get_summary(self, data: Dict[str, Any], ai_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Get AI summary of the plan changes.
        
        Args:
            data: Plan analysis results
            ai_config: AI configuration dictionary
            
        Returns:
            Optional[str]: AI-generated summary or None if AI is not configured
        """
        if not ai_config or 'resources' not in data:
            return None

        try:
            summarizer = self._get_ai_summarizer(ai_config)
            if not summarizer:
                return None

            resource_changes = self._convert_to_resource_changes(data['resources'])
            if not resource_changes:
                return None

            return asyncio.run(summarizer.summarize(resource_changes))
        except Exception as e:
            self.logger.error(f"AI summarization failed: {str(e)}")
            return None 