import logging
import argparse
from .plan_analyzer import LocalPlanAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Add argument parser
    parser = argparse.ArgumentParser(description='Analyze Terraform plan file')
    parser.add_argument('-i', '--input', 
                       required=True,
                       help='Path to the plan file to analyze')
    
    args = parser.parse_args()
    
    analyzer = LocalPlanAnalyzer()
    try:
        report = analyzer.generate_report(args.input)
        analyzer.print_report(report)
    except FileNotFoundError:
        logger.error("Plan file not found")
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    main() 