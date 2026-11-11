"""Offline package setup must not silently depend on a warm developer cache."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from job_application_engine.rendering import packages


def asset_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    root = tmp_path / "assets"
    package = root / "preview" / "fontawesome" / packages.FONT_AWESOME_VERSION
    package.mkdir(parents=True)
    content = b"synthetic pinned package"
    (package / "lib.typ").write_bytes(content)
    monkeypatch.setattr(
        packages, "FONT_AWESOME_FILES", {"lib.typ": hashlib.sha256(content).hexdigest()}
    )
    monkeypatch.setenv("JAE_TYPST_PACKAGE_ROOT", str(root))
    bundled = tmp_path / "bundled"
    bundled.mkdir()
    (bundled / "typst.toml").write_text('version = "0.3.0"')
    (bundled / "lib.typ").write_text("synthetic bundled package")
    return root, bundled


def test_local_packages_use_typst_namespace_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, bundled = asset_fixture(tmp_path, monkeypatch)
    stage = tmp_path / "stage"
    stage.mkdir()
    result = packages.prepare_typst_packages(stage, bundled)
    assert (result / "preview/rendercv/0.3.0/lib.typ").read_text() == "synthetic bundled package"
    assert (result / "preview/fontawesome/0.6.0/lib.typ").read_bytes() == packages.checked_assets(
        root
    )["lib.typ"]


def test_changed_or_missing_package_cannot_reach_compiler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, bundled = asset_fixture(tmp_path, monkeypatch)
    path = root / "preview/fontawesome/0.6.0/lib.typ"
    path.write_bytes(b"changed")
    with pytest.raises(packages.PackageAssetsError, match="checksum"):
        packages.prepare_typst_packages(tmp_path / "stage", bundled)
    assert not (tmp_path / "stage").exists()
    path.unlink()
    with pytest.raises(packages.PackageAssetsError, match="missing"):
        packages.prepare_typst_packages(tmp_path / "stage", bundled)


def test_explicit_setup_is_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JAE_TYPST_PACKAGE_ROOT", raising=False)
    with pytest.raises(packages.PackageAssetsError, match="explicit asset setup"):
        packages.prepare_typst_packages(tmp_path / "stage", tmp_path / "bundled")
