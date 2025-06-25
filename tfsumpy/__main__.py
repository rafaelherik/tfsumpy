import logging
import argparse
import warnings
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from .plan.analyzer import PlanAnalyzer
from .plan.reporter import PlanReporter
from .context import Context, ConfigurationError
from tfsumpy.plugins import load_plugins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default models for each provider
DEFAULT_MODELS = {
    'openai': 'gpt-3.5-turbo',  # Using standard model for small plans
    'gemini': 'gemini-pro',
    'anthropic': 'claude-3-sonnet-20240229'
}

# Default configuration values
DEFAULT_CONFIG = {
    'max_tokens': 2000,  # Reduced for small plans
    'temperature': 0.1,  # Low temperature for consistency
    'timeout': 60,  # Standard timeout
    'chunk_size': 20  # Increased chunk size for small plans
}

class TFSumpyError(Exception):
    """Base exception for TFSumpy errors"""
    pass

class ConfigurationError(TFSumpyError):
    """Raised when there is an error in configuration"""
    pass

class ValidationError(TFSumpyError):
    """Raised when input validation fails"""
    pass

def validate_plan_file(plan_path: str) -> None:
    """Validate that the plan file exists and is readable
    
    Args:
        plan_path: Path to the Terraform plan file
        
    Raises:
        ValidationError: If the plan file is invalid
    """
    plan_path = Path(plan_path)
    if not plan_path.exists():
        raise ValidationError(f"Plan file not found: {plan_path}")
    if not plan_path.is_file():
        raise ValidationError(f"Plan path is not a file: {plan_path}")
    if not os.access(plan_path, os.R_OK):
        raise ValidationError(f"Plan file is not readable: {plan_path}")

def get_ai_config(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """Get AI configuration from arguments and environment variables
    
    Args:
        args: Command line arguments
        
    Returns:
        Optional[Dict[str, Any]]: AI configuration if enabled
        
    Raises:
        ValidationError: If AI configuration is invalid
    """
    if not args.ai:
        return None
        
    if len(args.ai) < 2:
        raise ValidationError("--ai requires both provider and API key")
    
    provider = args.ai[0].lower()
    if provider not in DEFAULT_MODELS:
        raise ValidationError(f"Unsupported AI provider: {provider}")
    
    # Try to get API key from environment variable first
    api_key = os.getenv(f"TFSUMPY_{provider.upper()}_API_KEY", args.ai[1])
    if not api_key:
        raise ValidationError(f"API key not provided for {provider}")
    
    return {
        'provider': provider,
        'model': args.ai_model or DEFAULT_MODELS[provider],
        'api_key': api_key,
        'max_tokens': args.ai_max_tokens or DEFAULT_CONFIG['max_tokens'],
        'temperature': args.ai_temperature or DEFAULT_CONFIG['temperature'],
        'timeout': args.ai_timeout or DEFAULT_CONFIG['timeout'],
        'chunk_size': args.ai_chunk_size or DEFAULT_CONFIG['chunk_size'],
        'system_prompt': args.ai_system_prompt
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze Terraform plan files')
    parser.add_argument('plan_path', help='Path to the Terraform plan file')
    
    # Configuration arguments
    parser.add_argument('--config', help='Path to the configuration JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Output format options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-o', '--output', 
                            choices=['default', 'markdown', 'json'],
                            default='default',
                            help='Output format (default: default)')
    output_group.add_argument('--detailed', 
                            action='store_true',
                            help='Show detailed resource information')
    output_group.add_argument('--hide-changes',
                            action='store_true',
                            help='Hide detailed attribute changes')
    
    # AI summarization options
    ai_group = parser.add_argument_group('AI Summarization Options')
    ai_group.add_argument('--ai',
                         nargs='+',
                         metavar=('PROVIDER', 'API_KEY'),
                         help='Enable AI summarization with provider and API key (e.g., --ai openai YOUR_KEY)')
    ai_group.add_argument('--ai-model',
                         help='AI model to use (default varies by provider)')
    ai_group.add_argument('--ai-max-tokens',
                         type=int,
                         default=2048,
                         help='Maximum tokens for AI response (default: 2048)')
    ai_group.add_argument('--ai-temperature',
                         type=float,
                         default=0.1,
                         help='Temperature for AI response (default: 0.1)')
    ai_group.add_argument('--ai-timeout',
                         type=int,
                         default=60,
                         help='Timeout in seconds for AI API calls (default: 60)')
    ai_group.add_argument('--ai-chunk-size',
                         type=int,
                         default=20,
                         help='Number of resources to process in each chunk (default: 20)')
    ai_group.add_argument('--ai-system-prompt',
                         help='Custom system prompt for AI')
    
    # Deprecated arguments (kept for backward compatibility)
    deprecated_group = parser.add_argument_group('Deprecated Options')
    deprecated_group.add_argument('--changes', 
                                action='store_true',
                                help='[DEPRECATED] Show detailed attribute changes. Use --hide-changes instead.')
    deprecated_group.add_argument('--details', 
                                action='store_true',
                                help='[DEPRECATED] Show resource details. Use --detailed instead.')
    deprecated_group.add_argument('--markdown', 
                                action='store_true',
                                help='[DEPRECATED] Output the summary in markdown format. Use --output markdown instead.')
    
    # Plugin directory
    parser.add_argument(
        '--plugin-dir',
        default=os.getenv('TFSUMPY_PLUGIN_DIR', 'plugins'),
        help='Directory to load plugins from (default: plugins or TFSUMPY_PLUGIN_DIR env var)'
    )
    # Azure integration options
    azure_group = parser.add_argument_group('Azure Integration Options')
    azure_group.add_argument(
        '--azure',
        action='store_true',
        help='Enable Azure integration for AI analysis (requires azure-subscription-id)'
    )
    azure_group.add_argument(
        '--azure-subscription-id',
        help='Azure Subscription ID for Azure integration',
        default=os.getenv('AZURE_SUBSCRIPTION_ID')
    )
    azure_group.add_argument(
        '--azure-resource-groups',
        nargs='*',
        help='Azure resource group names to retrieve info for (default: all)'
    )
    azure_group.add_argument(
        '--azure-include-resources',
        action='store_true',
        help='Include Azure resources information for analysis'
    )
    
    args = parser.parse_args()
    
    # Handle deprecated arguments
    if args.changes:
        warnings.warn("--changes is deprecated and will be removed in a future version. Use --hide-changes instead.", 
                     DeprecationWarning, stacklevel=2)
    if args.details:
        warnings.warn("--details is deprecated and will be removed in a future version. Use --detailed instead.", 
                     DeprecationWarning, stacklevel=2)
    if args.markdown:
        warnings.warn("--markdown is deprecated and will be removed in a future version. Use --output markdown instead.", 
                     DeprecationWarning, stacklevel=2)
    
    try:
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Validate plan file
        validate_plan_file(args.plan_path)
        
        # Initialize Context and register analyzers
        context = Context(config_path=args.config, debug=args.debug)
        
        # Load plugins
        load_plugins(context, plugin_dir=args.plugin_dir)
        
        # Register analyzers and their corresponding reporters
        plan_analyzer = PlanAnalyzer(context=context)
        plan_reporter = PlanReporter()
        context.register_analyzer(plan_analyzer)
        context.register_reporter(plan_reporter)

        # Run analyzers and their reports
        plan_results = context.run_analyzers("plan", plan_path=args.plan_path)
        
        # Handle output format with backward compatibility
        output_format = args.output
        if args.markdown:
            output_format = 'markdown'
        
        # Get AI configuration
        ai_config = get_ai_config(args)
        # Azure integration configuration for AI analysis
        azure_config = None
        if args.azure:
            # Ensure subscription ID is provided
            if not args.azure_subscription_id:
                raise ValidationError(
                    "--azure requires --azure-subscription-id or AZURE_SUBSCRIPTION_ID env var"
                )
            azure_config = {
                'subscription_id': args.azure_subscription_id,
                'filter_resource_groups': args.azure_resource_groups or [],
                'include_resources': args.azure_include_resources
            }
        
        # Handle different output formats
        if output_format == 'markdown':
            plan_reporter.print_report_markdown(
                plan_results[0].data,
                show_changes=not args.hide_changes,
                show_details=args.detailed or args.details,
                ai_config=ai_config,
                azure_config=azure_config
            )
        elif output_format == 'json':
            # JSON output with optional AI and Azure analysis
            plan_reporter.print_report_json(
                plan_results[0].data,
                show_changes=not args.hide_changes,
                show_details=args.detailed or args.details,
                ai_config=ai_config,
                azure_config=azure_config
            )
        else:  # default console output
            # Console output with optional AI analysis
            context.run_reports(
                "plan",
                plan_results[0].data,
                show_changes=not args.hide_changes,
                show_details=args.detailed or args.details,
                ai_config=ai_config,
                azure_config=azure_config
            )
        
        # Store plan data for other analyzers
        context.set_plan_data(plan_results[0].data)
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except TFSumpyError as e:
        logger.error(f"TFSumpy error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        if args.debug:
            logger.exception("Detailed error information:")
        sys.exit(1)

if __name__ == '__main__':
    main() 