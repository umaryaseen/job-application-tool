"""Prepare pinned local Typst packages without network or global-cache lookup."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

FONT_AWESOME_VERSION = "0.6.0"
FONT_AWESOME_COMMIT = "4bb5c83d64f4a62a852c817ee6d92b3f94759950"
FONT_AWESOME_FILES = {
    "LICENSE": "0320baf81952401aa54110ac90787587119ce6a26fc2235e506f3cc150399162",
    "lib-gen-func.typ": "fafbe72def8d291bd79f6a48ebde87eb2197ba7c54d10dfca78cbaf8bf4e351d",
    "lib-gen-map.typ": "f088eb6ae7b072ad567a8238373eece12da9163bebdcb10b226a3aa4c728b75a",
    "lib-impl.typ": "d9d19a96f1c57fac4070c5caec9d14b6ece872f711874f803c2bb38085b2fd3a",
    "lib.typ": "411354321c70c4c8630954745420e8ee12603e24c8519bf54d89cd5c9b0d2877",
    "typst.toml": "59dd687a1f75ce0fd69cb0f2d6c2e701fdbeb971e04f6dfd0314e29177b5e502",
}


class PackageAssetsError(ValueError):
    """An explicitly installed local package is missing or changed."""


def checked_assets(root: Path) -> dict[str, bytes]:
    directory = root / "preview" / "fontawesome" / FONT_AWESOME_VERSION
    result = {}
    for name, expected in FONT_AWESOME_FILES.items():
        path = directory / name
        if not path.is_file() or path.is_symlink():
            raise PackageAssetsError("offline Typst package file is missing")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise PackageAssetsError("offline Typst package checksum mismatch")
        result[name] = data
    return result


def prepare_typst_packages(stage: Path, bundled: Path) -> Path:
    configured = os.environ.get("JAE_TYPST_PACKAGE_ROOT")
    if not configured or not Path(configured).is_absolute():
        raise PackageAssetsError("set JAE_TYPST_PACKAGE_ROOT after explicit asset setup")
    assets = checked_assets(Path(configured))
    root = stage / "typst-packages"
    rendercv = root / "preview" / "rendercv" / "0.3.0"
    rendercv.mkdir(parents=True)
    # RenderCV 2.8 bundles these files but not the namespace directory layout
    # required by Typst. Do not rely on a developer's warm global package cache.
    for name in ("typst.toml", "lib.typ"):
        (rendercv / name).write_bytes((bundled / name).read_bytes())
    fontawesome = root / "preview" / "fontawesome" / FONT_AWESOME_VERSION
    fontawesome.mkdir(parents=True)
    for name, data in assets.items():
        (fontawesome / name).write_bytes(data)
    return root
