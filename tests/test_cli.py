from __future__ import annotations

from pathlib import Path

import pytest

from job_application_engine.cli import main
from job_application_engine.config import ConfigurationError, private_data_root, safe_private_path


def test_help_and_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as help_exit:
        main(["--help"])
    assert help_exit.value.code == 0
    help_output = capsys.readouterr().out
    assert "usage: jae" in help_output
    with pytest.raises(SystemExit) as version_exit:
        main(["--version"])
    assert version_exit.value.code == 0
    assert "jae 0.1.0" in capsys.readouterr().out


def test_unknown_command_has_usage(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["unknown"])
    assert error.value.code == 2
    assert "usage: jae" in capsys.readouterr().err


def test_private_root_requires_explicit_absolute_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("JAE_DATA_DIR", raising=False)
    with pytest.raises(ConfigurationError, match="required"):
        private_data_root()
    relative = tmp_path / "relative"
    relative.mkdir()
    with pytest.raises(ConfigurationError, match="absolute"):
        private_data_root("relative")


def test_private_root_rejects_repository_and_symlink(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="outside"):
        private_data_root(Path.cwd())
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    with pytest.raises(ConfigurationError, match="symlink"):
        private_data_root(link)


def test_safe_private_path_rejects_escape_and_symlink(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir()
    assert safe_private_path("profiles/demo.json", root) == root / "profiles/demo.json"
    with pytest.raises(ConfigurationError, match="escapes"):
        safe_private_path("../outside", root)
    target = tmp_path / "target"
    target.mkdir()
    (root / "link").symlink_to(target, target_is_directory=True)
    with pytest.raises(ConfigurationError, match="symlink"):
        safe_private_path("link/file.txt", root)


def test_safe_private_path_validates_explicit_root(tmp_path: Path) -> None:
    root = tmp_path / "private"
    root.mkdir()
    assert safe_private_path("profile.json", root) == root / "profile.json"

    link = tmp_path / "root-link"
    link.symlink_to(root, target_is_directory=True)
    with pytest.raises(ConfigurationError, match="symlink"):
        safe_private_path("profile.json", link)

    file_root = tmp_path / "not-a-directory"
    file_root.write_text("synthetic", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="existing directory"):
        safe_private_path("profile.json", file_root)

    with pytest.raises(ConfigurationError, match="outside"):
        safe_private_path("profile.json", Path.cwd())
