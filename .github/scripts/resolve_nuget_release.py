"""Resolve a published GitHub release to its immutable SDK commit and version."""

import base64
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from verify_nuget_release import validate_version

REPOSITORY = "rudderlabs/rudder-sdk-.net"
API = f"https://api.github.com/repos/{REPOSITORY}"


def get(path, token):
    try:
        with urlopen(Request(API + path, headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"}), timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        raise ValueError(f"Cannot resolve published release: GitHub HTTP {error.code}") from error


def resolve(tag, event_name, event_release, token, fetch=get):
    if not tag.startswith("v"):
        raise ValueError("A v-prefixed release tag is required")
    version = tag[1:]
    validate_version(version)
    if event_name == "workflow_dispatch":
        if (os.environ.get("GITHUB_REF") != "refs/heads/master" or
                os.environ.get("GITHUB_REF_TYPE") != "branch"):
            raise ValueError("Manual dispatch must execute the workflow on master, not a tag")
        if event_release:
            raise ValueError("Manual dispatch must not include release event metadata")
    elif event_name == "release":
        if (os.environ.get("GITHUB_REF") != f"refs/tags/{tag}" or
                os.environ.get("GITHUB_REF_TYPE") != "tag"):
            raise ValueError("Release event ref does not match the release tag")
        if event_release.get("tag_name") != tag:
            raise ValueError("Release event tag does not match the requested tag")
    else:
        raise ValueError("Only release and manual validation events are supported")

    release = fetch(f"/releases/tags/{tag}", token)
    if (release.get("tag_name") != tag or release.get("draft") or
            not release.get("published_at") or release.get("name") not in (tag, f"Release {tag}")):
        raise ValueError("Tag does not identify a published release with matching version metadata")
    if event_name == "release" and (release.get("id") != event_release.get("id") or
                                   release.get("target_commitish") != event_release.get("target_commitish")):
        raise ValueError("Release event does not match the published release")

    ref = fetch(f"/git/ref/tags/{tag}", token)
    obj = ref.get("object", {})
    if ref.get("ref") != f"refs/tags/{tag}" or obj.get("type") not in ("tag", "commit"):
        raise ValueError("Release tag could not be resolved")
    if obj["type"] == "tag":
        obj = fetch(f"/git/tags/{obj['sha']}", token).get("object", {})
    if obj.get("type") != "commit" or not re.fullmatch(r"[0-9a-f]{40}", obj.get("sha", "")):
        raise ValueError("Release tag must resolve to a commit")
    sha = obj["sha"]
    target = release.get("target_commitish")
    if target not in (tag, sha, "master"):
        # GitHub allows a release created from a tag to retain its original
        # target branch name; the tag itself remains the immutable authority.
        raise ValueError("Published release target does not match its tag commit")
    if event_name == "release" and os.environ.get("GITHUB_SHA") != sha:
        raise ValueError("Release event commit does not match the tag commit")

    manifest = fetch(f"/contents/VERSION?ref={sha}", token)
    if manifest.get("encoding") != "base64":
        raise ValueError("Could not read VERSION at release commit")
    try:
        content = manifest["content"].replace("\n", "").replace("\r", "")
        file_version = base64.b64decode(content, validate=True).decode("utf-8").strip()
    except (KeyError, ValueError) as error:
        raise ValueError("Invalid VERSION at release commit") from error
    if file_version != version:
        raise ValueError("Release tag and VERSION at the tag commit do not agree")
    return version, sha


def main():
    tag = os.environ.get("RELEASE_TAG", "")
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    version, sha = resolve(tag, event_name, event.get("release", {}), os.environ["GITHUB_TOKEN"])
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"version={version}\nsha={sha}\ntag={tag}\n")
    print(f"Published release {tag} resolves to {sha} (RudderAnalytics {version})")


if __name__ == "__main__":
    main()
