"""Release path regressions without publishing or posting to Slack."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import validate_nuget_release_ref as release_ref


WORKFLOWS = Path(__file__).resolve().parents[1] / "workflows"
PUBLISHER = (WORKFLOWS / "publish-nuget.yml").read_text()
E2E = (WORKFLOWS / "published-sdk-e2e.yml").read_text()


def job(workflow, name):
    match = re.search(rf"^  {re.escape(name)}:\s*\n", workflow, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Missing job {name}")
    next_job = re.search(r"^  [\w-]+:\s*\n", workflow[match.end():], re.MULTILINE)
    return workflow[match.end():match.end() + next_job.start() if next_job else None]


class PublishNugetWorkflowTests(unittest.TestCase):
    def test_rejected_prerelease_cannot_reach_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "VERSION").write_text("1.2.3-beta.1\n")
            environment = os.environ.copy()
            environment.update(GITHUB_EVENT_NAME="release", GITHUB_REF_TYPE="tag",
                               GITHUB_REF_NAME="v1.2.3-beta.1", RELEASE_TAG="v1.2.3-beta.1")
            result = subprocess.run(
                [sys.executable, str(Path(release_ref.__file__))], cwd=directory,
                env=environment, capture_output=True, text=True, check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported package version", result.stderr)

        gate = job(PUBLISHER, "validate-ref")
        self.assertIn("validate_nuget_release_ref.py", gate)
        self.assertIn("needs: validate-ref", job(PUBLISHER, "pack"))
        publish = job(PUBLISHER, "publish")
        self.assertIn("needs: pack", publish)
        self.assertIn("NuGet/login@", publish)
        self.assertIn("--skip-duplicate", publish)

    def test_release_ref_requires_matching_stable_tag(self):
        self.assertEqual(release_ref.validate_ref("release", "tag", "v1.2.3", "v1.2.3", "1.2.3"), "1.2.3")
        for event, ref_type, ref_name, tag, version in (
            ("release", "tag", "v1.2.3-beta.1", "v1.2.3-beta.1", "1.2.3-beta.1"),
            ("release", "branch", "master", "v1.2.3", "1.2.3"),
            ("release", "tag", "v1.2.3", "v1.2.4", "1.2.3"),
            ("workflow_dispatch", "branch", "master", "master", "1.2.3"),
        ):
            with self.subTest(tag=tag, event=event, ref_type=ref_type), self.assertRaises(ValueError):
                release_ref.validate_ref(event, ref_type, ref_name, tag, version)

    def test_registry_then_full_e2e_then_release_only_notification(self):
        self.assertIn("needs: publish", job(PUBLISHER, "verify-publication"))
        acceptance = job(PUBLISHER, "published-e2e")
        self.assertIn("needs: verify-publication", acceptance)
        self.assertIn("needs.verify-publication.outputs.version", acceptance)
        notification = job(PUBLISHER, "notify-slack")
        self.assertIn("github.event_name == 'release'", notification)
        self.assertIn("needs.publish.result == 'success'", notification)
        self.assertIn("published; validation failed or incomplete", notification)
        self.assertIn("date -u +%Y-%m-%d", notification)
        self.assertIn("<!subteam^S03SW7DM8P3>", notification)
        self.assertIn("steps.slack_root.outputs.response", notification)
        self.assertIn("reply_broadcast: false", notification)
        self.assertEqual(notification.count("unfurl_links: false"), 2)

        retry = job(E2E, "validate")
        self.assertIn("runs-on: ubuntu-latest", retry)
        self.assertIn("suite: full", retry)
        self.assertIn("package-version: ${{ steps.release.outputs.version }}", retry)
        self.assertNotIn("NuGet/login", E2E)
        self.assertNotIn("dotnet nuget push", E2E)
        self.assertNotIn("slack-github-action", E2E)


if __name__ == "__main__":
    unittest.main()
