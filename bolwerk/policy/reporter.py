from typing import Any
from ..reporter import ReporterInterface
from ..reporters.base_reporter import BaseReporter
from .models import PolicyReport

class PolicyReporter(BaseReporter, ReporterInterface):
    """Handles formatting and display of policy compliance results."""
    
    @property
    def category(self) -> str:
        return "policy"
    
    def get_report(self, data: Any, **kwargs) -> PolicyReport:
        """Return the policy report object.
        
        Args:
            data: Policy analysis results (expected to be PolicyReport)
            **kwargs: Additional options
            
        Returns:
            PolicyReport: The validated report object
            
        Raises:
            TypeError: If data is not a PolicyReport instance
        """
        if not isinstance(data, PolicyReport):
            raise TypeError("Expected PolicyReport instance")
        return data
    
    def print_report(self, data: Any, **kwargs) -> None:
        """Print the policy compliance report.
        
        Args:
            data: Policy analysis results (expected to be PolicyReport)
            **kwargs: Additional display options
        
        Raises:
            TypeError: If data is not a PolicyReport instance
        """
        report = self.get_report(data, **kwargs)

        if not report.findings:
            self._print_header("No policy violations found")
            return

        self._print_header("Policy Compliance Report")
        self._print_summary(report.findings)
        self._print_violations(report.findings)

    def _print_summary(self, findings) -> None:
        """Print summary of policy violations."""
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for finding in findings:
            severity_counts[finding.severity.lower()] += 1

        self._write("\nViolations Summary:\n")
        for severity, count in severity_counts.items():
            if count > 0:
                self._write(
                    f"{self._colorize(severity.upper(), severity)}: {count}\n"
                )

    def _print_violations(self, findings) -> None:
        """Print detailed policy violations."""
        if not findings:
            return

        self._write("\nDetailed Violations:\n")
        
        # Sort findings by severity (high -> medium -> low)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_findings = sorted(
            findings,
            key=lambda x: severity_order.get(x.severity.lower(), 99)
        )

        for finding in sorted_findings:
            severity = finding.severity.upper()
            self._write(f"\n{self._colorize(f'[{severity}]', finding.severity.lower())} "
                       f"Policy {finding.policy_id}\n")
            self._write(f"Resource: {finding.resource_id}\n")
            self._write(f"Message: {finding.message}\n")
            if finding.remediation:
                self._write(f"Remediation: {finding.remediation}\n") 