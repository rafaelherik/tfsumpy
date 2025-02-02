import logging
from typing import Dict, Any
from ..reporter import ReporterInterface
from ..reporters.base_reporter import BaseReporter
from .models import RiskReport, RiskFinding

class RiskReporter(BaseReporter, ReporterInterface):
    """Handles formatting and output of risk analysis results."""
    
    def __init__(self):
        """Initialize the risk reporter."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @property
    def category(self) -> str:
        """Return the reporter category."""
        return "risk"
    
    def get_report(self, data: Any, **kwargs) -> RiskReport:
        """Return the risk report object.
        
        Args:
            data: Risk analysis results (expected to be RiskReport)
            **kwargs: Additional options
            
        Returns:
            RiskReport: The validated report object
            
        Raises:
            TypeError: If data is not a RiskReport instance
        """
        if not isinstance(data, RiskReport):
            raise TypeError("Expected RiskReport instance")
        return data
    
    def print_report(self, data: Any, **kwargs) -> None:
        """Print the risk analysis report.
        
        Args:
            data: Risk analysis results (RiskReport object)
            **kwargs: Additional display options
        """
        try:
            report = self.get_report(data, **kwargs)
            
            if report.findings is None:
                logging.getLogger(__name__).error("Invalid report: findings cannot be None")
                self._write("\nRisk Analysis Report")
                self._write("=" * 50)
                self._write("\nNo risks identified.\n")
                return
            
            self._print_header("Risk Analysis Report")
            
            if not report.findings:
                self._write("\nNo risks identified.\n")
                return
            
            # Print summary
            self._write("\nRisk Summary:\n")
            summary = self._get_severity_counts(report.findings)
            for severity, count in summary.items():
                if count > 0:
                    self._write(f"{severity.upper()}: {count}\n")
            
            # Print detailed findings
            self._write("\nDetailed Findings:\n")
            for finding in report.findings:
                self._print_finding(finding)
                
        except Exception as e:
            self.logger.error(f"Error generating risk report: {str(e)}")
            self._write("\nError generating risk report. Please check logs for details.\n")

    def _get_severity_counts(self, findings: list[RiskFinding]) -> Dict[str, int]:
        """Count findings by severity level.
        
        Args:
            findings: List of risk findings
            
        Returns:
            Dictionary of severity counts
        """
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in findings:
            severity = finding.severity.upper()
            if severity in counts:
                counts[severity] += 1
        return counts

    def _print_finding(self, finding: RiskFinding) -> None:
        """Print a single finding with consistent formatting.
        
        Args:
            finding: Risk finding to print
        """
        self._write(f"\n{self._colorize(f'[{finding.severity.upper()}]', finding.severity)} "
                   f"{finding.message}\n")
        self._write(f"Resource: {finding.resource_id}\n")
        
        if finding.impact:
            self._write(f"Impact: {finding.impact}\n")
        if finding.mitigation:
            self._write(f"Mitigation: {finding.mitigation}\n") 