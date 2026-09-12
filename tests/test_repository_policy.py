from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_private_paths_are_ignored() -> None:
    paths = ["local-data/example.json", "private/profile.json", ".env", "output/result.pdf"]
    result = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", *paths], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert set(result.stdout.splitlines()) == set(paths)


def test_staged_safeguard_rejects_private_path_and_secret(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    (repo / "local-data").mkdir()
    (repo / "local-data" / "profile.txt").write_text("synthetic", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    sys.path.insert(0, str(ROOT))
    from scripts.check_staged import check

    assert any("private path" in item for item in check(repo))
    synthetic_secret = "github_pat_" + "12345678901234567890"
    (repo / "safe.txt").write_text(f"value='{synthetic_secret}'", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "safe.txt"], check=True)
    assert any("credential-like" in item for item in check(repo))
