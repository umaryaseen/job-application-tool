from __future__ import annotations

import shutil
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


def test_git_hook_installation_and_invocation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True
    )
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Synthetic Test"], check=True)
    shutil.copytree(ROOT / ".githooks", repo / ".githooks")
    (repo / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "check_staged.py", repo / "scripts" / "check_staged.py")
    subprocess.run([str(ROOT / "scripts" / "install_hooks.sh")], cwd=repo, check=True)
    subprocess.run([str(ROOT / "scripts" / "install_hooks.sh")], cwd=repo, check=True)
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "config", "--local", "--get", "core.hooksPath"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == ".githooks"
    )

    safe = repo / "safe.txt"
    safe.write_text("synthetic safe content", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "safe.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "safe synthetic commit"], check=True)

    secret = "github_pat_" + "12345678901234567890"
    safe.write_text(f"value='{secret}'", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "safe.txt"], check=True)
    safe.write_text("benign working tree content", encoding="utf-8")
    rejected = subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "secret"], capture_output=True, text=True
    )
    assert rejected.returncode != 0
    assert "credential-like content staged" in rejected.stderr

    subprocess.run(["git", "-C", str(repo), "reset", "-q"], check=True)
    private_file = repo / "local-data" / "profile.txt"
    private_file.parent.mkdir()
    private_file.write_text("synthetic private path", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-f", "local-data/profile.txt"], check=True)
    rejected = subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "private path"], capture_output=True, text=True
    )
    assert rejected.returncode != 0
    assert "private path staged" in rejected.stderr


def test_hook_setup_preserves_conflicting_local_configuration(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "--local", "core.hooksPath", "custom-hooks"], check=True
    )
    result = subprocess.run(
        [str(ROOT / "scripts" / "install_hooks.sh")], cwd=repo, capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "custom-hooks" in result.stderr
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "config", "--local", "--get", "core.hooksPath"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        == "custom-hooks"
    )
