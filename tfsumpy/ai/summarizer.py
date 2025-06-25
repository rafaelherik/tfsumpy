from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Protocol
import json
import re
import logging
import asyncio
from dataclasses import dataclass
from ..models import ResourceChange
try:
    import backoff
except ImportError:
    # Fallback dummy backoff for environments without backoff package
    class _DummyBackoff:
        # Dummy attributes for compatibility
        expo = None
        full_jitter = None
        @staticmethod
        def on_exception(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
    backoff = _DummyBackoff()

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Protocol):
    """Protocol defining the interface for AI providers."""
    async def generate_completion(self, prompt: str, content: str, max_tokens: int, temperature: float) -> str:
        """Generate a completion from the AI model."""
        pass

class OpenAIProvider:
    """OpenAI provider implementation."""
    def __init__(self, api_key: str, model: str):
        if AsyncOpenAI is None:
            raise ImportError("OpenAI package is not installed")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.base_timeout = 60

    @backoff.on_exception(
        backoff.expo,
        (Exception),
        max_tries=3,
        max_time=180,
        jitter=backoff.full_jitter
    )
    async def generate_completion(self, prompt: str, content: str, max_tokens: int, temperature: float) -> str:
        """Generate a completion from the OpenAI model with retry logic."""
        try:
            if not self.client.api_key:
                raise ValueError("OpenAI API key is not set")

            logger.debug(f"Making OpenAI API call with model {self.model}")
            logger.debug(f"Content length: {len(content)} characters")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=self.base_timeout
            )
            
            if not response.choices:
                raise ValueError("Empty response from OpenAI API")
                
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg:
                logger.error("OpenAI API authentication failed. Please check your API key.")
            elif "rate limit" in error_msg:
                logger.error("OpenAI API rate limit exceeded. Please try again later.")
            elif "timeout" in error_msg:
                logger.error(f"OpenAI API request timed out after {self.base_timeout} seconds")
            else:
                logger.error(f"OpenAI API call failed: {str(e)}")
            raise

class GeminiProvider:
    """Google Gemini provider implementation."""
    def __init__(self, api_key: str, model: str):
        if genai is None:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    async def generate_completion(self, prompt: str, content: str, max_tokens: int, temperature: float) -> str:
        try:
            response = await asyncio.wait_for(
                self.model.generate_content(
                    f"{prompt}\n\n{content}",
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                        "candidate_count": 1
                    }
                ),
                timeout=30
            )
            return response.text
        except asyncio.TimeoutError:
            logger.error(f"Gemini API call timed out after 30 seconds")
            raise TimeoutError("Gemini API call timed out")
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise

class AnthropicProvider:
    """Anthropic Claude provider implementation."""
    def __init__(self, api_key: str, model: str):
        if AsyncAnthropic is None:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate_completion(self, prompt: str, content: str, max_tokens: int, temperature: float) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=prompt,
                    messages=[
                        {"role": "user", "content": content}
                    ]
                ),
                timeout=30
            )
            return response.content[0].text
        except asyncio.TimeoutError:
            logger.error(f"Anthropic API call timed out after 30 seconds")
            raise TimeoutError("Anthropic API call timed out")
        except Exception as e:
            logger.error(f"Anthropic API call failed: {str(e)}")
            raise

@dataclass
class AnalysisResult:
    """Structured result of the AI analysis."""
    summary: Dict[str, Any]
    facts: List[Dict[str, Any]]
    categories: Dict[str, List[Dict[str, Any]]]
    risks: List[Dict[str, Any]]

@dataclass
class SummarizerConfig:
    """Configuration for AI summarization."""
    provider: str  # 'openai', 'gemini', or 'anthropic'
    model: str
    api_key: str
    max_tokens: int = 2048  # Set to 2048 for completion
    temperature: float = 0.1
    system_prompt: Optional[str] = None
    timeout: int = 60  # Default timeout in seconds

class BaseSummarizer(ABC):
    """Base class for AI summarizers."""
    
    def __init__(self, config: SummarizerConfig):
        self.config = config
        self._validate_config()
        self.provider = self._create_provider()
    
    def _validate_config(self):
        """Validate the configuration."""
        if not self.config.api_key:
            raise ValueError(f"API key is required for {self.config.provider}")
        if not self.config.model:
            raise ValueError(f"Model name is required for {self.config.provider}")
        if self.config.timeout < 1:
            raise ValueError("Timeout must be at least 1 second")

    def _create_provider(self) -> AIProvider:
        """Create the appropriate AI provider."""
        providers = {
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "anthropic": AnthropicProvider
        }
        
        if self.config.provider not in providers:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
        
        return providers[self.config.provider](self.config.api_key, self.config.model)

    def _get_combined_prompt(self) -> str:
        """Get a combined prompt for all analysis stages."""
        return """You are a Terraform expert. Analyze the provided Terraform changes and provide a comprehensive analysis.
IMPORTANT: You MUST return a valid JSON object with NO additional text, comments, or explanations before or after the JSON.
The JSON MUST be properly formatted and parseable. Here is the EXACT structure you must follow:

{
    "summary": {
        "total_resources": number,  // Must match the total_changes from input
        "changes_by_type": {
            "create": number,  // Must match the input counts
            "update": number,
            "delete": number
        },
        "impact_level": "Low/Medium/High",
        "key_components": ["list", "of", "main", "components"]
    },
    "facts": [
        {
            "fact": "string",
            "type": "create/update/delete",
            "resource": "string",
            "impact": "Low/Medium/High"
        }
    ],
    "categories": {
        "networking": [
            {
                "resource": "string",
                "change": "string",
                "impact": "Low/Medium/High"
            }
        ],
        "compute": [...],
        "storage": [...],
        "security": [...],
        "database": [...],
        "monitoring": [...]
    },
    "risks": [
        {
            "risk": "string",
            "level": "Low/Medium/High",
            "affected_resources": ["list", "of", "resources"],
            "mitigation": "string"
        }
    ]
}

Requirements:
1. Be precise with numbers and avoid speculation
2. Focus on concrete changes and their impacts
3. Group changes by infrastructure category
4. Identify specific risks and mitigation steps
5. Use consistent resource identifiers
6. Assess impact based on resource importance and change type
7. Return ONLY the JSON object, no other text
8. Compact the JSON to reduce the return size
9. Ensure all numbers match exactly with the input data"""

    def _clean_change_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and optimize change data to reduce token usage."""
        if not data:
            return {}
            
        # Only keep essential fields that are relevant for analysis
        essential_fields = {
            'name', 'type', 'provider', 'tags', 'count', 'for_each',
            'depends_on', 'lifecycle', 'description', 'status'
        }
        
        cleaned_data = {}
        for key, value in data.items():
            # Skip empty values
            if value is None or value == "":
                continue
                
            # Keep essential fields
            if key in essential_fields:
                cleaned_data[key] = value
                continue
                
            # For nested objects, recursively clean them
            if isinstance(value, dict):
                cleaned_nested = self._clean_change_data(value)
                if cleaned_nested:
                    cleaned_data[key] = cleaned_nested
            # For lists, clean each item if it's a dict
            elif isinstance(value, list):
                cleaned_list = [
                    self._clean_change_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
                if cleaned_list:
                    cleaned_data[key] = cleaned_list
                    
        return cleaned_data

    def _prepare_changes_for_analysis(self, changes: List[ResourceChange]) -> str:
        """Prepare changes for analysis with optimized data."""
        try:
            formatted_changes = []
            for change in changes:
                # Include all essential information for accurate analysis
                change_data = {
                    "action": change.action,
                    "resource_type": change.resource_type,
                    "identifier": change.identifier,
                    "name": change.name if hasattr(change, 'name') else change.identifier,
                    "data": self._clean_change_data(change.data) if change.data else {},
                    "changes": change.changes if hasattr(change, 'changes') else {},
                    "before": change.before if hasattr(change, 'before') else {},
                    "after": change.after if hasattr(change, 'after') else {}
                }
                formatted_changes.append(change_data)
            
            # Add metadata about the total changes
            analysis_data = {
                "total_changes": len(changes),
                "changes_by_action": {
                    "create": sum(1 for c in changes if c.action == "create"),
                    "update": sum(1 for c in changes if c.action == "update"),
                    "delete": sum(1 for c in changes if c.action == "delete")
                },
                "changes": formatted_changes
            }
            
            # Convert to JSON with minimal whitespace
            return json.dumps(analysis_data, separators=(',', ':'), default=str)
        except Exception as e:
            logger.error(f"Failed to prepare changes for analysis: {str(e)}")
            raise

    def _format_analysis_result(self, result: AnalysisResult) -> str:
        """Format the analysis result into a markdown report."""
        try:
            sections = []

            # Summary Section
            sections.append("### Change Overview")
            sections.append(f"- Total Resources: {result.summary['total_resources']}")
            sections.append("- Changes by Type:")
            for change_type, count in result.summary['changes_by_type'].items():
                sections.append(f"  - {change_type.title()}: {count}")
            sections.append(f"- Overall Impact: {result.summary['impact_level']}")
            sections.append("- Key Components:")
            for component in result.summary['key_components']:
                sections.append(f"  - {component}")

            # Facts Section
            sections.append("\n### Key Facts")
            for fact in result.facts:
                sections.append(f"- {fact['fact']} ({fact['type']})")
                sections.append(f"  - Resource: {fact['resource']}")
                sections.append(f"  - Impact: {fact['impact']}")

            # Categories Section
            sections.append("\n### Changes by Category")
            for category, changes in result.categories.items():
                if changes:
                    sections.append(f"\n#### {category.title()}")
                    for change in changes:
                        sections.append(f"- {change['resource']}")
                        sections.append(f"  - Change: {change['change']}")
                        sections.append(f"  - Impact: {change['impact']}")

            # Risks Section
            sections.append("\n### Potential Risks")
            for risk in result.risks:
                sections.append(f"- {risk['risk']} (Level: {risk['level']})")
                sections.append(f"  - Affected Resources: {', '.join(risk['affected_resources'])}")
                sections.append(f"  - Mitigation: {risk['mitigation']}")

            return "\n".join(sections)
        except Exception as e:
            logger.error(f"Failed to format analysis result: {str(e)}")
            raise

    async def _call_ai(self, changes: str) -> str:
        """Make a single AI call with the combined prompt."""
        try:
            return await self.provider.generate_completion(
                prompt=self._get_combined_prompt(),
                content=changes,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
        except TimeoutError as e:
            logger.error(f"AI call timed out: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"AI call failed: {str(e)}")
            raise

    @abstractmethod
    async def summarize(self, changes: List[ResourceChange]) -> str:
        """Summarize the changes using AI."""
        pass

class OpenAISummarizer(BaseSummarizer):
    """OpenAI-based summarizer."""
    
    def _get_facts_prompt(self) -> str:
        """Get prompt for facts analysis."""
        return """You are a Terraform expert. Analyze the provided Terraform changes and extract key facts.
IMPORTANT: You MUST return a valid JSON object with NO additional text. Here is the EXACT structure:

{
    "facts": [
        {
            "fact": "string",
            "type": "create/update/delete",
            "resource": "string",
            "impact": "Low/Medium/High"
        }
    ]
}

Requirements:
1. Be precise with numbers and avoid speculation
2. Focus on concrete changes and their impacts
3. Use consistent resource identifiers
4. Assess impact based on resource importance and change type
5. Return ONLY the JSON object, no other text"""

    def _get_categories_prompt(self) -> str:
        """Get prompt for categorization analysis."""
        return """You are a Terraform expert. Categorize the provided Terraform changes and identify risks.
IMPORTANT: You MUST return a valid JSON object with NO additional text. Here is the EXACT structure:

{
    "summary": {
        "total_resources": number,
        "changes_by_type": {
            "create": number,
            "update": number,
            "delete": number
        },
        "impact_level": "Low/Medium/High",
        "key_components": ["list", "of", "main", "components"]
    },
    "categories": {
        "networking": [
            {
                "resource": "string",
                "change": "string",
                "impact": "Low/Medium/High"
            }
        ],
        "compute": [...],
        "storage": [...],
        "security": [...],
        "database": [...],
        "monitoring": [...]
    },
    "risks": [
        {
            "risk": "string",
            "level": "Low/Medium/High",
            "affected_resources": ["list", "of", "resources"],
            "mitigation": "string"
        }
    ]
}

Requirements:
1. Be precise with numbers and avoid speculation
2. Group changes by infrastructure category
3. Identify specific risks and mitigation steps
4. Return ONLY the JSON object, no other text"""

    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            # Prepare the changes data
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            # Make separate API calls for different aspects of the analysis
            facts_json = await self.provider.generate_completion(
                prompt=self._get_facts_prompt(),
                content=cleaned_changes,
                max_tokens=1024,  # Smaller token limit for focused analysis
                temperature=self.config.temperature
            )
            
            categories_json = await self.provider.generate_completion(
                prompt=self._get_categories_prompt(),
                content=cleaned_changes,
                max_tokens=1024,  # Smaller token limit for focused analysis
                temperature=self.config.temperature
            )
            
            # Parse and validate the responses
            try:
                facts_analysis = json.loads(facts_json)
                categories_analysis = json.loads(categories_json)
                
                # Combine the analyses
                analysis = {
                    "summary": categories_analysis["summary"],
                    "facts": facts_analysis["facts"],
                    "categories": categories_analysis["categories"],
                    "risks": categories_analysis["risks"]
                }
                
                # Validate required fields
                required_fields = ["summary", "facts", "categories", "risks"]
                for field in required_fields:
                    if field not in analysis:
                        raise ValueError(f"Missing required field: {field}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {str(e)}")
                raise ValueError("Invalid JSON response from AI model")
            
            # Create analysis result
            result = AnalysisResult(
                summary=analysis["summary"],
                facts=analysis["facts"],
                categories=analysis["categories"],
                risks=analysis["risks"]
            )
            
            # Format the result
            return self._format_analysis_result(result)
            
        except Exception as e:
            logger.error(f"OpenAI summarization failed: {str(e)}")
            raise

class GeminiSummarizer(BaseSummarizer):
    """Google Gemini-based summarizer."""
    
    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            # Make a single API call for all analysis
            analysis_json = await self._call_ai(cleaned_changes)
            analysis = json.loads(analysis_json)
            
            # Create analysis result
            result = AnalysisResult(
                summary=analysis["summary"],
                facts=analysis["facts"],
                categories=analysis["categories"],
                risks=analysis["risks"]
            )
            
            # Format the result
            return self._format_analysis_result(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            raise ValueError("Invalid JSON response from AI model")
        except Exception as e:
            logger.error(f"Gemini summarization failed: {str(e)}")
            raise

class AnthropicSummarizer(BaseSummarizer):
    """Anthropic Claude-based summarizer."""
    
    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            # Make a single API call for all analysis
            analysis_json = await self._call_ai(cleaned_changes)
            analysis = json.loads(analysis_json)
            
            # Create analysis result
            result = AnalysisResult(
                summary=analysis["summary"],
                facts=analysis["facts"],
                categories=analysis["categories"],
                risks=analysis["risks"]
            )
            
            # Format the result
            return self._format_analysis_result(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            raise ValueError("Invalid JSON response from AI model")
        except Exception as e:
            logger.error(f"Anthropic summarization failed: {str(e)}")
            raise

def create_summarizer(config: SummarizerConfig) -> BaseSummarizer:
    """Factory function to create the appropriate summarizer."""
    providers = {
        "openai": OpenAISummarizer,
        "gemini": GeminiSummarizer,
        "anthropic": AnthropicSummarizer
    }
    
    if config.provider not in providers:
        raise ValueError(f"Unsupported provider: {config.provider}")
    
    return providers[config.provider](config)

def create_deterministic_config(provider: str, model: str, api_key: str) -> SummarizerConfig:
    """Create a configuration optimized for deterministic results."""
    return SummarizerConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        max_tokens=2048,  # Set to 2048 for completion
        temperature=0.1,  # Low temperature for consistency
        system_prompt=None,  # Use the built-in deterministic prompt
        timeout=60  # Standard timeout
    )