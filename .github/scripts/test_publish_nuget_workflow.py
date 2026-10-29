"""Release path regressions without publishing or posting to Slack."""

import json
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


def run_step(job_body, name):
    match = re.search(rf"^      - name: {re.escape(name)}\n", job_body, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Missing step {name}")
    next_step = re.search(r"^      - name: ", job_body[match.end():], re.MULTILINE)
    section = job_body[match.end():match.end() + next_step.start() if next_step else None]
    run = re.search(r"^        run: \|\n", section, re.MULTILINE)
    if run is None:
        raise AssertionError(f"Missing script for {name}")
    lines = []
    for line in section[run.end():].splitlines():
        if not line.startswith("          "):
            break
        lines.append(line[10:])
    return "\n".join(lines)


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
        self.assertIn("needs: [validate-ref, pack, publish, verify-publication, published-e2e]", notification)
        self.assertIn("if: ${{ always() && github.event_name == 'release' }}", notification)
        self.assertIn("published; validation failed or incomplete", notification)
        self.assertIn("date -u +%Y-%m-%d", notification)
        self.assertIn("<!subteam^S03SW7DM8P3>", notification)
        self.assertIn("steps.slack_root.outputs.response", notification)
        self.assertIn("reply_broadcast: false", notification)
        self.assertEqual(notification.count("unfurl_links: false"), 2)

        retry = job(E2E, "validate")
        self.assertRegex(retry, r"uses: rudderlabs/github-action-sdk-e2e/\.github/workflows/published-sdk-e2e\.yml@[0-9a-f]{40}")
        self.assertNotIn("steps:", retry)
        self.assertIn("package-version: ${{ inputs.package-version || github.ref_name }}", retry)
        self.assertIn("release-app-client-id: ${{ vars.RELEASE_APP_CLIENT_ID }}", retry)
        self.assertIn("RELEASE_PRIVATE_KEY: ${{ secrets.RELEASE_PRIVATE_KEY }}", retry)
        self.assertNotIn("NuGet/login", E2E)
        self.assertNotIn("dotnet nuget push", E2E)
        self.assertNotIn("slack-github-action", E2E)

    def test_final_notifications_distinguish_negative_outcomes(self):
        notification = job(PUBLISHER, "notify-slack")
        summary_script = run_step(notification, "Record publication and acceptance separately")
        root_script = run_step(notification, "Prepare release notification")
        thread_script = run_step(notification, "Prepare release details thread")
        cases = (
            (("success", "success", "success", "success", "success"), "released; validation complete"),
            (("success", "success", "success", "success", "failure"), "published; validation failed or incomplete"),
            (("success", "success", "success", "failure", "skipped"), "publication unconfirmed; validation incomplete"),
            (("success", "success", "failure", "skipped", "skipped"), "publication failed or unconfirmed"),
            (("success", "failure", "skipped", "skipped", "skipped"), "publication failed before upload"),
            (("failure", "skipped", "skipped", "skipped", "skipped"), "publication failed before upload"),
        )
        for results, expected in cases:
            with self.subTest(results=results), tempfile.TemporaryDirectory() as directory:
                environment = os.environ.copy()
                environment.update(zip(("REF_RESULT", "PACK_RESULT", "PUBLISH_RESULT",
                                        "PUBLIC_VERIFICATION", "ACCEPTANCE_RESULT"), results))
                environment.update(RUNNER_TEMP=directory, GITHUB_STEP_SUMMARY=str(Path(directory, "summary")),
                                   SLACK_CHANNEL_ID="C123", RELEASE_TAG="v1.2.3",
                                   SLACK_RESPONSE='{"ok":true,"ts":"1234567890.123456"}',
                                   RELEASE_RUN_URL="https://github.com/rudderlabs/rudder-sdk-.net/actions/runs/123")
                for script in (summary_script, root_script, thread_script):
                    subprocess.run(["bash", "-e", "-c", script], env=environment,
                                   capture_output=True, text=True, check=True)
                root = json.loads(Path(directory, "nuget-release-notification.json").read_text())
                thread = json.loads(Path(directory, "nuget-release-thread.json").read_text())
                summary = Path(directory, "summary").read_text()
                self.assertIn(expected, root["text"])
                self.assertNotIn("https://", root["text"])
                self.assertRegex(root["text"], r"\.NET SDK v1\.2\.3 \| \d{4}-\d{2}-\d{2} \|")
                self.assertIn("<!subteam^S03SW7DM8P3>", root["text"])
                self.assertEqual(thread["thread_ts"], "1234567890.123456")
                self.assertFalse(thread["reply_broadcast"])
                self.assertFalse(thread["unfurl_links"])
                self.assertFalse(thread["unfurl_media"])
                self.assertIn(f"Exact public registry artifact: {results[3]}", thread["text"])
                self.assertIn(f"Pack: {results[1]}", thread["text"])
                self.assertIn(f"NuGet publish: {results[2]}", thread["text"])
                self.assertIn(f"Full E2E delivery and cleanup: {results[4]}", thread["text"])
                if results[3] == "success" and results[4] != "success":
                    self.assertIn("remains published", summary)
                else:
                    self.assertNotIn("remains published", summary)


if __name__ == "__main__":
    unittest.main()
