"""Verify public NuGet availability without credentials or publication writes."""

import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SERVICE_INDEX = "https://api.nuget.org/v3/index.json"
PACKAGE = "rudderanalytics"


def validate_version(version, release_tag=""):
    # The SDK uses three-part versions, optionally with a prerelease suffix.
    number = r"(?:0|[1-9][0-9]*)"
    if not re.fullmatch(rf"{number}\.{number}\.{number}(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", version):
        raise ValueError(f"Unsupported package version: {version!r}")
    if release_tag and release_tag != f"v{version}":
        raise ValueError(f"Release tag {release_tag!r} does not match VERSION {version!r}")
    return version.lower()


def request(url, method="GET"):
    with urlopen(Request(url, method=method), timeout=15) as response:
        return response.read() if method == "GET" else None


def check_available(version, fetch=request):
    service = json.loads(fetch(SERVICE_INDEX))
    base = next(resource["@id"] for resource in service["resources"]
                if resource["@type"] == "PackageBaseAddress/3.0.0")
    if not base.startswith("https://"):
        raise ValueError("NuGet package base address must use HTTPS")
    package_base = f"{base.rstrip('/')}/{PACKAGE}"
    versions = json.loads(fetch(f"{package_base}/index.json"))["versions"]
    if version not in versions:
        return False
    # Confirm the exact version's package file is downloadable, not just indexed.
    fetch(f"{package_base}/{version}/{PACKAGE}.{version}.nupkg", method="HEAD")
    return True


def verify(version, delay=30, timeout=3600, check=check_available,
           sleep=time.sleep, clock=time.monotonic):
    deadline = clock() + timeout
    reason = "verification deadline reached"
    while clock() < deadline:
        try:
            if check(version):
                print(f"RudderAnalytics {version} is available on NuGet.", flush=True)
                return
            reason = "exact version is not indexed yet"
        except HTTPError as error:
            reason = f"NuGet returned HTTP {error.code}"
        except (URLError, TimeoutError, OSError, ValueError, KeyError, StopIteration) as error:
            reason = f"NuGet verification request failed ({type(error).__name__})"
        remaining = deadline - clock()
        print(f"Waiting for NuGet: {reason}; "
              f"{max(0, remaining):.0f}s remaining", flush=True)
        if remaining <= 0:
            break
        sleep(min(delay, remaining))
    raise RuntimeError(f"Could not verify RudderAnalytics {version}: {reason}")


def main():
    version = Path("VERSION").read_text().strip()
    tag = os.environ.get("RELEASE_TAG", "")
    if os.environ.get("GITHUB_EVENT_NAME") == "release" and not tag:
        raise ValueError("Release event is missing its tag")
    normalized = validate_version(version, tag)
    verify(normalized)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"version={version}\n")


if __name__ == "__main__":
    main()
