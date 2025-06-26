import subprocess, sys, json

def test_cli_smoke():
    result = subprocess.run(
        [sys.executable, "-m", "tfsumpy", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage" in result.stdout.lower()
