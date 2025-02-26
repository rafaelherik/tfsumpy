import logging
import argparse
from pathlib import Path
from .plan.analyzer import PlanAnalyzer
from .plan.reporter import PlanReporter
from .risk.analyzer import RiskAnalyzer
from .risk.reporter import RiskReporter
from .policy.analyzer import PolicyAnalyzer
from .policy.reporter import PolicyReporter
from .context import Context

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
    
    # Module enablement
    parser.add_argument('--risks', action='store_true', help='Enable risk assessment')
    parser.add_argument('--policies', action='store_true', help='Enable policy compliance check')
    
    args = parser.parse_args()
    
    try:
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Initialize Context and register analyzers
        context = Context(config_path=args.config, debug=args.debug)
        
        # Register analyzers and their corresponding reporters
        plan_analyzer = PlanAnalyzer(context=context)
        plan_reporter = PlanReporter()
        context.register_analyzer(plan_analyzer)
        context.register_reporter(plan_reporter)
        
        if args.risks:
            risk_analyzer = RiskAnalyzer()
            risk_reporter = RiskReporter()
            context.register_analyzer(risk_analyzer)
            context.register_reporter(risk_reporter)
            
        if args.policies:
            policy_analyzer = PolicyAnalyzer(db_manager=context.db_manager)
            policy_reporter = PolicyReporter()
            context.register_analyzer(policy_analyzer)
            context.register_reporter(policy_reporter)
        
        # Run analyzers and their reports
        plan_results = context.run_analyzers("plan", plan_path=args.plan_path)
        context.run_reports("plan", plan_results[0].data, 
                          show_changes=args.changes, 
                          show_details=args.details)
        
        # Store plan data for other analyzers
        context.set_plan_data(plan_results[0].data)
        
        if args.risks:
            risk_results = context.run_analyzers("risk")
            context.run_reports("risk", risk_results[0].data)
        
        if args.policies:
            policy_results = context.run_analyzers("policy")
            context.run_reports("policy", policy_results[0].data)
        
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