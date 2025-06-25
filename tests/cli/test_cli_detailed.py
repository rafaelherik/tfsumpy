import sys
import warnings
import re
import pytest
from pathlib import Path
from tfsumpy.__main__ import main


@pytest.fixture
def sample_plan():
    """Path to the sample Terraform plan JSON file."""
    # Locate repository root from this test file
    project_root = Path(__file__).parents[2]
    plan_path = project_root / "samples" / "sample1.json"
    return str(plan_path)

def test_cli_shows_all_changes(capsys, monkeypatch, sample_plan):
    """Test that running with --detailed shows all resource changes."""
    monkeypatch.setattr(sys, "argv", ["tfsumpy", sample_plan, "--detailed"])
    # Run CLI and capture output
    main()
    out = capsys.readouterr().out
    # Strip ANSI color codes for assertions
    plain = re.compile(r'\x1b\[[0-9;]*m').sub('', out)
    # Verify each action type and symbol appears
    assert "CREATE aws_s3_bucket" in plain
    assert "+" in plain
    assert "UPDATE aws_instance" in plain
    assert "~" in plain
    assert "DELETE aws_security_group" in plain
    assert "-" in plain

def test_cli_alias_details_shows_all_changes(capsys, monkeypatch, sample_plan):
    """Test that deprecated --details alias shows resource changes."""
    # Suppress deprecation warnings in stderr
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    monkeypatch.setattr(sys, "argv", ["tfsumpy", sample_plan, "--details"])
    main()
    out = capsys.readouterr().out
    plain = re.compile(r'\x1b\[[0-9;]*m').sub('', out)
    assert "CREATE aws_s3_bucket" in plain
    assert "+" in plain
    assert "UPDATE aws_instance" in plain
    assert "~" in plain
    assert "DELETE aws_security_group" in plain
    assert "-" in plain