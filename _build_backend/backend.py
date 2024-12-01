from __future__ import annotations

import os

from scikit_build_core import build as _orig

if hasattr(_orig, "prepare_metadata_for_build_editable"):
    prepare_metadata_for_build_editable = _orig.prepare_metadata_for_build_editable
if hasattr(_orig, "prepare_metadata_for_build_wheel"):
    prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_editable = _orig.build_editable
build_wheel = _orig.build_wheel
build_sdist = _orig.build_sdist
get_requires_for_build_editable = _orig.get_requires_for_build_editable
get_requires_for_build_sdist = _orig.get_requires_for_build_sdist

def get_requires_for_build_wheel(config_settings=None):
    packages_orig = _orig.get_requires_for_build_wheel(config_settings)
    if os.environ.get("NINJA_PYTHON_DIST_ALLOW_NINJA_DEP", "0") != "0":
        return packages_orig
    packages = []
    for package in packages_orig:
        package_name = package.lower().split(">")[0].strip()
        if package_name == "ninja":
            # never request ninja from the ninja build
            continue
        packages.append(package)
    return packages
