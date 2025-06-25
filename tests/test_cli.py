import sys
import json
import re
import pytest
from pathlib import Path
from tfsumpy.__main__ import main, ValidationError

# Regex to strip ANSI escape sequences
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

@pytest.fixture(scope='module')
def samples_dir():
    # Samples directory in project root
    return Path(__file__).parents[1] / 'samples'

@pytest.mark.parametrize('sample_file', [
    'sample1.json',
    'azure_landing_zone_plan.json',
])
def test_cli_default_and_detailed_flags(sample_file, samples_dir, capsys, monkeypatch):
    """
    Test CLI default output and --detailed flag across both sample plans.
    Default (--detailed=False) should show summary and changes.
    Detailed (--detailed) should include resources section.
    """
    plan_path = str(samples_dir / sample_file)
    # Default output: no flags
    monkeypatch.setattr(sys, 'argv', ['tfsumpy', plan_path])
    # Should not raise
    main()
    out = capsys.readouterr().out
    plain = _ANSI_RE.sub('', out)
    # Basic header and summary present
    assert 'Terraform Plan Analysis' in plain
    assert 'Total Changes:' in plain
    # Resource changes section should appear by default (show_changes=True)
    assert 'Resources Changes:' in plain

    # Detailed flag: same behavior (resources always shown when changes shown)
    monkeypatch.setattr(sys, 'argv', ['tfsumpy', plan_path, '--detailed'])
    main()
    out2 = capsys.readouterr().out
    plain2 = _ANSI_RE.sub('', out2)
    assert 'Resources Changes:' in plain2

@pytest.mark.parametrize('flags', [
    ['--hide-changes'],
    ['--hide-changes', '--detailed'],
])
@pytest.mark.parametrize('sample_file', ['sample1.json', 'azure_landing_zone_plan.json'])
def test_cli_hide_changes_hides_diff(flags, sample_file, samples_dir, capsys, monkeypatch):
    """--hide-changes should suppress attribute diffs but still show resources if detailed."""
    plan_path = str(samples_dir / sample_file)
    monkeypatch.setattr(sys, 'argv', ['tfsumpy', plan_path] + flags)
    main()
    out = capsys.readouterr().out
    plain = _ANSI_RE.sub('', out)
    # If detailed or default, resources header appears only if show_changes or show_details
    show_details = '--detailed' in flags
    if show_details:
        assert 'Resources Changes:' in plain
    else:
        # hide-changes and no detailed => no resources section
        assert 'Resources Changes:' not in plain
    # No diff symbols when hide-changes
    assert '+' not in plain
    assert '~' not in plain
    # Delete symbol '-' may appear in header or summary, but no attribute deletions
    # We check absence of lines starting with two spaces then '-'
    assert not any(line.startswith('  -') for line in plain.splitlines())

@pytest.mark.parametrize('fmt', ['json', 'markdown'])
@pytest.mark.parametrize('sample_file', ['sample1.json', 'azure_landing_zone_plan.json'])
def test_cli_output_formats(fmt, sample_file, samples_dir, capsys, monkeypatch):
    """Test JSON and Markdown outputs parse and contain expected sections."""
    plan_path = str(samples_dir / sample_file)
    monkeypatch.setattr(sys, 'argv', ['tfsumpy', plan_path, '--output', fmt])
    main()
    out = capsys.readouterr().out
    plain = _ANSI_RE.sub('', out)
    lines = plain.splitlines()
    # Last line is the written-to-file message
    last = lines[-1]
    # Prefix differs for JSON (upper) vs Markdown (capitalized)
    prefix = f"{fmt.upper() if fmt=='json' else fmt.capitalize()} report written to:"
    assert last.startswith(prefix)
    content = '\n'.join(lines[:-1])
    if fmt == 'json':
        # Should be valid JSON
        data = json.loads(content)
        assert 'summary' in data and 'resources' in data
        # resources list length should equal summary total_resources
        assert len(data['resources']) == data['summary']['total_resources']
    else:
        # Markdown
        assert content.startswith('# Terraform Plan Analysis Report')
        assert '## Summary' in content
        assert '## Resource Changes' in content