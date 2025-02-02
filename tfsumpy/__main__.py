import logging
import argparse
from .plan_analyzer import LocalPlanAnalyzer
from .context import Context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze Terraform plan files')
    parser.add_argument('plan_path', help='Path to the Terraform plan file')
    parser.add_argument('--config', help='Path to the rules configuration JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--show-module', action='store_true', help='Show resources grouped by module')
    parser.add_argument('--show-changes', action='store_true', help='Show detailed attribute changes for resources')
    parser.add_argument('--risks', action='store_true', help='Show risk assessment section')
    parser.add_argument('--details', action='store_true', help='Show resource details section')
    
    args = parser.parse_args()
    
    # Create Context object first
    context = Context(config_path=args.config, debug=args.debug)
    
    # Pass context to LocalPlanAnalyzer
    analyzer = LocalPlanAnalyzer(context=context)
    report = analyzer.generate_report(args.plan_path)
    analyzer.print_report(
        report, 
        show_module=args.show_module, 
        show_changes=args.show_changes,
        show_risks=args.risks,
        show_details=args.details
    )

if __name__ == '__main__':
    main() 