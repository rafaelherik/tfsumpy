import logging
import argparse
import warnings
from pathlib import Path
from .plan.analyzer import PlanAnalyzer
from .plan.reporter import PlanReporter
from .context import Context
from tfsumpy.plugins import load_plugins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    parser.add_argument('--plugin-dir', default='plugins', help='Directory to load plugins from')
    
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
        
        # Handle different output formats
        if output_format == 'markdown':
            plan_reporter.print_report_markdown(plan_results[0].data,
                                              show_changes=not args.hide_changes,
                                              show_details=args.detailed or args.details)
        elif output_format == 'json':
            plan_reporter.print_report_json(plan_results[0].data,
                                          show_changes=not args.hide_changes,
                                          show_details=args.detailed or args.details)
        else:  # default output
            context.run_reports("plan", plan_results[0].data,
                              show_changes=not args.hide_changes,
                              show_details=args.detailed or args.details)
        
        # Store plan data for other analyzers
        context.set_plan_data(plan_results[0].data)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if args.debug:
            logger.exception("Detailed error information:")
        exit(1)

if __name__ == '__main__':
    main() 