"""Reject unsupported release refs before packing or NuGet authentication."""

import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from verify_nuget_release import validate_version


def validate_ref(event, ref_type, ref_name, release_tag, version):
    if event not in ("release", "workflow_dispatch") or ref_type != "tag":
        raise ValueError("Publication requires a release tag ref")
    if release_tag != ref_name:
        raise ValueError("Release metadata and workflow ref identify different tags")
    return validate_version(version, release_tag)


def require_published_release(repository, tag, token, api_url):
    request = Request(
        f"{api_url.rstrip('/')}/repos/{repository}/releases/tags/{quote(tag, safe='')}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urlopen(request, timeout=30) as response:
        release = json.load(response)
    if (release.get("tag_name") != tag or release.get("draft") is not False
            or release.get("prerelease") is not False or not release.get("published_at")):
        raise ValueError("Manual publication requires the matching published stable GitHub release")


def main():
    version = Path("VERSION").read_text().strip()
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    validate_ref(
        event,
        os.environ.get("GITHUB_REF_TYPE", ""),
        os.environ.get("GITHUB_REF_NAME", ""),
        os.environ.get("RELEASE_TAG", ""),
        version,
    )
    if event == "workflow_dispatch":
        require_published_release(
            os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REF_NAME"],
            os.environ["GITHUB_TOKEN"], os.environ["GITHUB_API_URL"],
        )


if __name__ == "__main__":
    main()
