import subprocess
import sys


def test_cli_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "--help"],
        capture_output=True,
        text=True,
        cwd="/Users/luanluan/Workspace/bot-analysis-script",
    )
    assert result.returncode == 0
    assert "--draft" in result.stdout
    assert "--style" in result.stdout
    assert "--create-images" in result.stdout
