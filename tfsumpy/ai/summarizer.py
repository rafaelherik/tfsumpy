from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
import re
from dataclasses import dataclass
from ..models import ResourceChange

@dataclass
class SummarizerConfig:
    """Configuration for AI summarization."""
    provider: str  # 'openai', 'gemini', or 'anthropic'
    model: str
    api_key: str
    max_tokens: int = 1000
    temperature: float = 0.1  # Lower temperature for more deterministic results
    system_prompt: Optional[str] = None

class BaseSummarizer(ABC):
    """Base class for AI summarizers."""
    
    def __init__(self, config: SummarizerConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration."""
        if not self.config.api_key:
            raise ValueError(f"API key is required for {self.config.provider}")
        if not self.config.model:
            raise ValueError(f"Model name is required for {self.config.provider}")
    
    def _prepare_changes_for_analysis(self, changes: List[ResourceChange]) -> str:
        """Prepare changes for analysis while preserving original structure and counts."""
        # Preserve original data structure but format for readability
        formatted_changes = []
        
        for change in changes:
            # Keep the original structure but ensure it's serializable
            change_data = {
                "action": change.action,
                "resource_type": change.resource_type,
                "identifier": change.identifier,
                "data": change.data if change.data else {}
            }
            formatted_changes.append(change_data)
        
        # Create a summary for context
        summary_stats = {
            "total_changes": len(changes),
            "actions": {},
            "resource_types": {}
        }
        
        for change in changes:
            # Count actions
            action = change.action
            summary_stats["actions"][action] = summary_stats["actions"].get(action, 0) + 1
            
            # Count resource types
            resource_type = change.resource_type
            summary_stats["resource_types"][resource_type] = summary_stats["resource_types"].get(resource_type, 0) + 1
        
        # Combine summary and detailed changes
        analysis_data = {
            "summary": summary_stats,
            "changes": formatted_changes
        }
        
        return json.dumps(analysis_data, indent=2, default=str)
    
    def _get_system_prompt(self) -> str:
        """Get the deterministic system prompt for the AI model."""
        if self.config.system_prompt:
            return self.config.system_prompt
        
        return """You are a Terraform expert. Analyze the provided Terraform plan changes and create a detailed summary in markdown format.

The input contains a summary with accurate counts and the complete original change data. Use the summary counts for accurate reporting.

FORMATTING RULES:
- Use bullet points (-) for ALL lists and sections
- No numbered lists allowed anywhere in the response
- Use markdown headers (###) for main sections
- Keep technical accuracy while ensuring readability
- Be consistent in terminology and phrasing

REQUIRED STRUCTURE - Include ALL sections even if empty:

### Summary
- Total number of resources affected (use the exact count from summary.total_changes)
- Breakdown of change types using exact counts from summary.actions
- Key infrastructure components involved
- Overall risk level (Low/Medium/High)

### Changes Analysis
- Resources being created and their purpose
- Existing resources being modified and what's changing specifically
- Resources being removed and cleanup implications
- Critical dependencies between resources

### Risk Assessment
- High-priority risks that could cause service disruption
- Security implications of the changes
- Data loss or corruption possibilities
- Performance impact concerns
- Breaking changes that affect dependent systems

### Recommendations
- Essential pre-deployment validation steps
- Recommended deployment approach and timing
- Required monitoring during deployment
- Rollback procedures and contingency plans
- Team coordination requirements

### Impact Assessment
- Operational impact on running systems and services
- Financial implications including cost changes
- End-user impact and service availability
- Compliance and security posture changes
- Integration points that may be affected

ANALYSIS REQUIREMENTS:
- Use exact counts from the provided summary data
- Focus on actionable and specific insights
- Highlight breaking changes with clear warnings
- Explain technical changes in business context
- Prioritize information by criticality and urgency
- Use consistent language for similar resource types
- If no relevant information exists for a section, state "No significant items identified"
- Always end each section with a brief summary statement

Provide clear, deterministic analysis focusing on practical deployment considerations."""
    
    @abstractmethod
    async def summarize(self, changes: List[ResourceChange]) -> str:
        """Summarize the changes using AI."""
        pass

class OpenAISummarizer(BaseSummarizer):
    """OpenAI-based summarizer."""
    
    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.config.api_key)
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            response = await client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Analyze these Terraform changes:\n\n{cleaned_changes}"}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                seed=42  # For more deterministic results
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI summarization failed: {str(e)}")

class GeminiSummarizer(BaseSummarizer):
    """Google Gemini-based summarizer."""
    
    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(
                self.config.model,
                system_instruction=self._get_system_prompt()
            )
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            response = await model.generate_content(
                f"Analyze these Terraform changes:\n\n{cleaned_changes}",
                generation_config={
                    "max_output_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "candidate_count": 1  # For deterministic results
                }
            )
            
            return response.text
            
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Gemini summarization failed: {str(e)}")

class AnthropicSummarizer(BaseSummarizer):
    """Anthropic Claude-based summarizer."""
    
    async def summarize(self, changes: List[ResourceChange]) -> str:
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.config.api_key)
            cleaned_changes = self._prepare_changes_for_analysis(changes)
            
            response = await client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": f"Analyze these Terraform changes:\n\n{cleaned_changes}"}
                ]
            )
            
            return response.content[0].text
            
        except ImportError:
            raise ImportError("Anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic summarization failed: {str(e)}")

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

# Usage example with deterministic configuration
def create_deterministic_config(provider: str, model: str, api_key: str) -> SummarizerConfig:
    """Create a configuration optimized for deterministic results."""
    return SummarizerConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        max_tokens=1500,  # Increased for comprehensive analysis
        temperature=0.1,  # Low temperature for consistency
        system_prompt=None  # Use the built-in deterministic prompt
    )