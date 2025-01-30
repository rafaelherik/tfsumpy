import logging
import argparse
from .plan_analyzer import LocalPlanAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Analyze Terraform plan files')
    parser.add_argument('plan_path', help='Path to the Terraform plan file')
    parser.add_argument('--config', help='Path to the rules configuration JSON file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    analyzer = LocalPlanAnalyzer(config_path=args.config, debug=args.debug)
    report = analyzer.generate_report(args.plan_path)
    analyzer.print_report(report)

if __name__ == '__main__':
    main() 