# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""mkdocs hook — surface the repo's top-level ``figures/`` directory in the
built site without duplicating the PNGs into ``docs/``.

Experiments write their outputs to ``figures/`` (single source of truth, used
by the README and the standalone runs). The docs pages live under ``docs/``.
Without a hook, an experiment doc that referenced ``../../figures/foo.png``
would resolve outside ``docs_dir`` and be rejected by strict-mode mkdocs.

This hook registers every ``figures/*.png`` as a build file at the site path
``figures/<name>.png``, so a doc at ``docs/experiments/foo.md`` can embed it
as ``![alt](../figures/foo.png)`` and have the link resolve cleanly under
strict mode.
"""
from __future__ import annotations
import pathlib
from mkdocs.structure.files import File


def on_files(files, config):
    docs_dir = pathlib.Path(config["docs_dir"])
    repo_root = docs_dir.parent
    figdir = repo_root / "figures"
    if not figdir.is_dir():
        return files
    for png in sorted(figdir.glob("*.png")):
        files.append(File(
            path=f"figures/{png.name}",
            src_dir=str(repo_root),
            dest_dir=config["site_dir"],
            use_directory_urls=config["use_directory_urls"],
        ))
    return files
