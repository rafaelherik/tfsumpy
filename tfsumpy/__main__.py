import logging
import argparse
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
    
    # Display options for plan analysis
    parser.add_argument('--changes', action='store_true', help='Show detailed attribute changes')
    parser.add_argument('--details', action='store_true', help='Show resource details')
    parser.add_argument('--markdown', action='store_true', help='Output the summary in markdown format')
    
    # Plugin directory
    parser.add_argument('--plugin-dir', default='plugins', help='Directory to load plugins from')
    
    args = parser.parse_args()
    
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
        if args.markdown:
            plan_reporter.print_report_markdown(plan_results[0].data,
                                               show_changes=args.changes,
                                               show_details=args.details)
        else:
            context.run_reports("plan", plan_results[0].data, 
                              show_changes=args.changes, 
                              show_details=args.details)
        
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