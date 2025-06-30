import subprocess, sys, os
import pytest


@pytest.mark.skip("Interactive CLI – test invocation only")
def test_cli_invocation():
    # Just ensure the module imports and main runs with --help equivalent
    process = subprocess.run([sys.executable, "-m", "nina_project.app.cli"], input=b"exit\n", capture_output=True, timeout=5)
    assert process.returncode == 0 