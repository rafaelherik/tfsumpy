import logging
import argparse
from pathlib import Path
from .plan_analyzer import LocalPlanAnalyzer
from .report import PlanReporter
from .context import Context
from .policy import POLICY_FEATURE_ENABLED, PolicyDBManager, PolicyLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze Terraform plan files')
    parser.add_argument('plan_path', help='Path to the Terraform plan file')
    
    # Configuration arguments
    parser.add_argument('--config', help='Path to the rules configuration JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Display options
    parser.add_argument('--show-module', action='store_true', help='Show resources grouped by module')
    parser.add_argument('--show-changes', action='store_true', help='Show detailed attribute changes for resources')
    parser.add_argument('--show-risks', action='store_true', help='Show risk assessment section')
    parser.add_argument('--show-details', action='store_true', help='Show resource details section')
    
    # Policy management
    parser.add_argument('--policy-dir', help='Directory containing policy YAML files')
    parser.add_argument('--policy-file', help='Single policy YAML file to load')
    parser.add_argument('--clear-policies', action='store_true', help='Clear all existing policies before loading new ones')
    
    args = parser.parse_args()
    
    try:
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize Context
        context = Context(config_path=args.config, debug=args.debug)
        
        # Initialize policy components if policy management is requested
        if args.policy_dir or args.policy_file or args.clear_policies:
            if not POLICY_FEATURE_ENABLED:
                logger.warning("Policy management is currently disabled and will be available in a future release")
            else:
                db_manager = PolicyDBManager()
                policy_loader = PolicyLoader(db_manager)
                
                # Clear policies if requested
                if args.clear_policies:
                    logger.info("Clearing existing policies")
                    db_manager.clear_policies()
                
                # Load policies from directory
                if args.policy_dir:
                    logger.info(f"Loading policies from directory: {args.policy_dir}")
                    policy_loader.load_policy_directory(args.policy_dir)
                
                # Load single policy file
                if args.policy_file:
                    logger.info(f"Loading policy file: {args.policy_file}")
                    policy_loader.load_policy_file(args.policy_file)
                
                # Attach policy database to context
                context.policy_db = db_manager
        
        # Initialize analyzer and reporter
        analyzer = LocalPlanAnalyzer(context=context)
        reporter = PlanReporter()
        
        # Generate and print report
        report = analyzer.generate_report(args.plan_path)
        reporter.print_report(
            report,
            show_module=args.show_module,
            show_changes=args.show_changes,
            show_risks=args.show_risks,
            show_details=args.show_details or args.show_changes
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if args.debug:
            logger.exception("Detailed error information:")
        exit(1)

if __name__ == '__main__':
    main() 