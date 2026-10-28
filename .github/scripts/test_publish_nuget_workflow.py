"""Release gate checks: no publish or notification on a failed validation path."""

from pathlib import Path
import unittest

import yaml

WORKFLOW = Path(__file__).parents[1] / "workflows" / "publish-nuget.yml"


class PublishWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load(WORKFLOW.read_text())
        cls.jobs = cls.workflow["jobs"]

    def test_only_published_release_or_explicit_manual_mode(self):
        triggers = self.workflow["on"]
        self.assertEqual(triggers["release"]["types"], ["published"])
        dispatch = triggers["workflow_dispatch"]["inputs"]
        self.assertEqual(dispatch["mode"]["options"], ["publish", "validate-only"])
        self.assertTrue(dispatch["release_tag"]["required"])
        resolver = (Path(__file__).parent / "resolve_nuget_release.py").read_text()
        self.assertIn('"refs/heads/master"', resolver)
        self.assertIn("Manual dispatch must execute", resolver)
        self.assertNotIn("tags or master", resolver)
        self.assertFalse(self.workflow["concurrency"]["cancel-in-progress"])

    def test_tag_validation_happens_before_pack_and_upload(self):
        self.assertEqual(self.jobs["pack"]["needs"], "validate-ref")
        self.assertEqual(self.jobs["publish"]["needs"], ["validate-ref", "pack"])
        self.assertIn("inputs.mode == 'publish'", self.jobs["pack"]["if"])
        self.assertIn("inputs.mode == 'publish'", self.jobs["publish"]["if"])
        validation = self.jobs["validate-ref"]["steps"]
        self.assertEqual(validation[-1]["run"], "python3 .github/scripts/resolve_nuget_release.py")
        self.assertEqual(validation[-1]["env"]["RELEASE_TAG"],
                         "${{ github.event.release.tag_name || inputs.release_tag }}")
        self.assertNotIn("ref", validation[-2]["with"])
        checkout = next(step for step in self.jobs["pack"]["steps"] if
                        step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["ref"], "${{ needs.validate-ref.outputs.sha }}")
        self.assertTrue(any("RELEASE_VERSION" in step.get("env", {}) and
                            "Packed artifact" in step.get("run", "")
                            for step in self.jobs["pack"]["steps"]))

    def test_validate_only_skips_pack_login_and_upload_but_checks_exact_package(self):
        self.assertIn("needs.publish.result == 'skipped'", self.jobs["verify"]["if"])
        self.assertIn("inputs.mode == 'validate-only'", self.jobs["verify"]["if"])
        steps = self.jobs["verify"]["steps"]
        self.assertFalse(any("NuGet/login" in step.get("uses", "") or
                             "nuget push" in step.get("run", "") or
                             "dotnet pack" in step.get("run", "") for step in steps))
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        # A historical release may not have the verifier script or its new
        # exact-version guard. Run trusted code from the executing workflow.
        self.assertEqual(checkout["with"]["ref"], "${{ github.workflow_sha }}")
        verifier = steps[-1]
        self.assertEqual(verifier["env"]["EXPECTED_VERSION"], "${{ needs.validate-ref.outputs.version }}")
        self.assertEqual(verifier["env"]["RELEASE_TAG"], "${{ needs.validate-ref.outputs.tag }}")
        self.assertEqual(verifier["run"], "python3 .github/scripts/verify_nuget_release.py")
        self.assertEqual(self.jobs["validate-ref"]["outputs"]["sha"],
                         "${{ steps.release.outputs.sha }}")
        self.assertEqual(self.jobs["validate-ref"]["outputs"]["version"],
                         "${{ steps.release.outputs.version }}")

    def test_public_verification_precedes_full_acceptance_then_release_notification(self):
        self.assertEqual(self.jobs["accept-published"]["needs"], ["validate-ref", "verify"])
        self.assertIn("needs.verify.result == 'success'", self.jobs["accept-published"]["if"])
        self.assertEqual(self.jobs["notify"]["needs"], ["verify", "accept-published"])
        self.assertIn("github.event_name == 'release'", self.jobs["notify"]["if"])
        self.assertIn("needs.accept-published.result == 'success'", self.jobs["notify"]["if"])
        self.assertEqual(self.jobs["notify"]["steps"][1]["env"]["RELEASE_VERSION"],
                         "${{ needs.verify.outputs.version }}")
        # Until upstream published-mode support exists, acceptance must fail
        # rather than silently dispatch source-candidate E2E for master.
        fail_step = self.jobs["accept-published"]["steps"][1]
        self.assertIn("exit 1", fail_step["run"])
        self.assertIn("SDK-5961/SDK-5962", fail_step["run"])


if __name__ == "__main__":
    unittest.main()
