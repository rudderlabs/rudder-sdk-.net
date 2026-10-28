import base64
import os
import unittest
from unittest.mock import Mock, patch

import resolve_nuget_release as resolver

SHA = "a" * 40
TAG_SHA = "b" * 40
TAG = "v2.0.3"


def responses(tag=TAG, version="2.0.3", target=SHA, published="2026-09-25T15:22:43Z"):
    return {
        f"/releases/tags/{tag}": {"id": 17, "tag_name": tag, "name": tag,
                                    "published_at": published, "draft": False,
                                    "target_commitish": target},
        f"/git/ref/tags/{tag}": {"ref": f"refs/tags/{tag}",
                                   "object": {"type": "tag", "sha": TAG_SHA}},
        f"/git/tags/{TAG_SHA}": {"object": {"type": "commit", "sha": SHA}},
        f"/contents/VERSION?ref={SHA}": {"encoding": "base64", "content":
                                          base64.b64encode(version.encode()).decode()},
    }


class ResolveNuGetReleaseTests(unittest.TestCase):
    def test_manual_master_uses_release_tag_not_current_master(self):
        data = responses(target="master")
        fetch = Mock(side_effect=lambda path, token: data[path])
        with patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
            self.assertEqual(resolver.resolve(TAG, "workflow_dispatch", {}, "token", fetch),
                             ("2.0.3", SHA))
        paths = [call.args[0] for call in fetch.call_args_list]
        self.assertIn(f"/contents/VERSION?ref={SHA}", paths)
        self.assertNotIn("/contents/VERSION?ref=master", paths)

    def test_wrapped_contents_api_base64_resolves_version(self):
        data = responses()
        content = data[f"/contents/VERSION?ref={SHA}"]["content"]
        data[f"/contents/VERSION?ref={SHA}"]["content"] = content[:5] + "\n" + content[5:] + "\n"
        with patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
            self.assertEqual(resolver.resolve(TAG, "workflow_dispatch", {}, "token",
                                              lambda path, token: data[path]), ("2.0.3", SHA))

    def test_invalid_contents_api_base64_fails_closed(self):
        data = responses()
        data[f"/contents/VERSION?ref={SHA}"]["content"] = "%%%\n"
        with patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
            with self.assertRaisesRegex(ValueError, "Invalid VERSION"):
                resolver.resolve(TAG, "workflow_dispatch", {}, "token",
                                 lambda path, token: data[path])

    def test_release_event_uses_tag_commit_not_workflow_sha_guess(self):
        data = responses()
        fetch = Mock(side_effect=lambda path, token: data[path])
        with patch.dict(os.environ, {"GITHUB_REF": f"refs/tags/{TAG}", "GITHUB_REF_TYPE": "tag", "GITHUB_SHA": SHA}):
            self.assertEqual(resolver.resolve(TAG, "release", data[f"/releases/tags/{TAG}"],
                                              "token", fetch), ("2.0.3", SHA))

    def test_reject_manual_tag_ref_before_any_api_request(self):
        fetch = Mock()
        with patch.dict(os.environ, {"GITHUB_REF": f"refs/tags/{TAG}", "GITHUB_REF_TYPE": "tag"}):
            with self.assertRaisesRegex(ValueError, "master"):
                resolver.resolve(TAG, "workflow_dispatch", {}, "token", fetch)
        fetch.assert_not_called()

    def test_reject_missing_unpublished_or_mismatched_release(self):
        for change, pattern in (
                ({"published_at": None}, "published release"),
                ({"draft": True}, "published release"),
                ({"tag_name": "v2.0.2"}, "published release"),
                ({"name": "v2.0.2"}, "published release"),
                ({"target_commitish": "unrelated-branch"}, "target")):
            with self.subTest(change=change), patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
                data = responses()
                data[f"/releases/tags/{TAG}"].update(change)
                fetch = Mock(side_effect=lambda path, token: data[path])
                with self.assertRaisesRegex(ValueError, pattern):
                    resolver.resolve(TAG, "workflow_dispatch", {}, "token", fetch)
        with patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
            with self.assertRaisesRegex(ValueError, "HTTP 404"):
                resolver.resolve(TAG, "workflow_dispatch", {}, "token",
                                 Mock(side_effect=ValueError("Cannot resolve published release: GitHub HTTP 404")))

    def test_reject_wrong_commit_and_version(self):
        for change, pattern in (({"version": "2.0.2"}, "VERSION"),
                                ({"sha": "not-a-commit"}, "resolve to a commit")):
            with self.subTest(change=change), patch.dict(os.environ, {"GITHUB_REF": "refs/heads/master", "GITHUB_REF_TYPE": "branch"}):
                data = responses(version=change.get("version", "2.0.3"))
                if "sha" in change:
                    data[f"/git/tags/{TAG_SHA}"]["object"]["sha"] = change["sha"]
                with self.assertRaisesRegex(ValueError, pattern):
                    resolver.resolve(TAG, "workflow_dispatch", {}, "token",
                                     lambda path, token: data[path])

    def test_reject_release_event_identity_or_ref_drift(self):
        data = responses()
        release = dict(data[f"/releases/tags/{TAG}"])
        with patch.dict(os.environ, {"GITHUB_REF": f"refs/tags/{TAG}", "GITHUB_REF_TYPE": "tag", "GITHUB_SHA": SHA}):
            with self.assertRaisesRegex(ValueError, "does not match"):
                resolver.resolve(TAG, "release", dict(release, id=18), "token",
                                 lambda path, token: data[path])
        with patch.dict(os.environ, {"GITHUB_REF": f"refs/tags/{TAG}", "GITHUB_REF_TYPE": "tag", "GITHUB_SHA": "c" * 40}):
            with self.assertRaisesRegex(ValueError, "commit does not match"):
                resolver.resolve(TAG, "release", release, "token",
                                 lambda path, token: data[path])


if __name__ == "__main__":
    unittest.main()
