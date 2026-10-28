"""Reject unsupported release refs before packing or NuGet authentication."""

import os
from pathlib import Path

from verify_nuget_release import validate_version


def validate_ref(event, ref_type, ref_name, release_tag, version):
    if event not in ("release", "workflow_dispatch") or ref_type != "tag":
        raise ValueError("Publication requires a release tag ref")
    if release_tag != ref_name:
        raise ValueError("Release metadata and workflow ref identify different tags")
    return validate_version(version, release_tag)


def main():
    version = Path("VERSION").read_text().strip()
    validate_ref(
        os.environ.get("GITHUB_EVENT_NAME", ""),
        os.environ.get("GITHUB_REF_TYPE", ""),
        os.environ.get("GITHUB_REF_NAME", ""),
        os.environ.get("RELEASE_TAG", ""),
        version,
    )


if __name__ == "__main__":
    main()
