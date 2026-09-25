import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import verify_nuget_release as verifier


class VerifyNuGetReleaseTests(unittest.TestCase):
    def test_release_tag_must_match(self):
        self.assertEqual(verifier.validate_version("2.0.3", "v2.0.3"), "2.0.3")
        with self.assertRaises(ValueError):
            verifier.validate_version("2.0.2", "v2.0.3")

    def test_reject_unsafe_or_unsupported_versions(self):
        for version in ("", "../../x", "2.0.3\nversion=bad", "02.0.3", "2.0.3+build"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                verifier.validate_version(version)

    def test_prerelease_is_lowercased_for_nuget(self):
        self.assertEqual(verifier.validate_version("2.0.3-RC.1"), "2.0.3-rc.1")

    def test_exact_version_and_download_url(self):
        fetch = Mock(side_effect=[
            b'{"resources":[{"@type":"PackageBaseAddress/3.0.0","@id":"https://api.nuget.org/v3-flatcontainer/"}]}',
            b'{"versions":["2.0.2","2.0.3"]}',
            None,
        ])
        self.assertTrue(verifier.check_available("2.0.3", fetch))
        fetch.assert_called_with(
            "https://api.nuget.org/v3-flatcontainer/rudderanalytics/2.0.3/rudderanalytics.2.0.3.nupkg",
            method="HEAD",
        )

    def test_other_version_does_not_pass(self):
        fetch = Mock(side_effect=[
            b'{"resources":[{"@type":"PackageBaseAddress/3.0.0","@id":"https://api.nuget.org/v3-flatcontainer/"}]}',
            b'{"versions":["2.0.30"]}',
        ])
        self.assertFalse(verifier.check_available("2.0.3", fetch))
        self.assertEqual(fetch.call_count, 2)

    def test_retries_until_index_and_package_are_available(self):
        missing_file = HTTPError("https://api.nuget.org", 404, "Not Found", {}, None)
        check = Mock(side_effect=[False, missing_file, True])
        sleep = Mock()
        verifier.verify("2.0.3", attempts=3, check=check, sleep=sleep)
        self.assertEqual(check.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_failure_is_bounded_and_reports_reason(self):
        for error, reason in ((False, "not indexed"),
                              (URLError("offline"), "request failed"),
                              (ValueError("bad JSON"), "request failed")):
            with self.subTest(error=error):
                check = Mock(side_effect=[error, error])
                sleep = Mock()
                with self.assertRaisesRegex(RuntimeError, reason):
                    verifier.verify("2.0.3", attempts=2, check=check, sleep=sleep)
                self.assertEqual(check.call_count, 2)
                sleep.assert_called_once_with(30)

    def test_default_window_allows_indexing_beyond_five_minutes(self):
        elapsed = [0]

        def sleep(seconds):
            elapsed[0] += seconds

        check = Mock(side_effect=lambda version: elapsed[0] >= 900)
        verifier.verify("2.0.3", check=check, sleep=sleep, clock=lambda: elapsed[0])
        self.assertEqual(elapsed[0], 900)
        self.assertEqual(check.call_count, 31)

    def test_default_window_stops_after_one_hour(self):
        elapsed = [0]

        def sleep(seconds):
            elapsed[0] += seconds

        check = Mock(return_value=False)
        with self.assertRaisesRegex(RuntimeError, "not indexed"):
            verifier.verify("2.0.3", check=check, sleep=sleep, clock=lambda: elapsed[0])
        self.assertEqual(elapsed[0], 3600)
        self.assertEqual(check.call_count, 121)

    def test_request_time_counts_toward_deadline(self):
        elapsed = [0]

        def check(version):
            elapsed[0] += 45
            raise URLError("timeout")

        def sleep(seconds):
            elapsed[0] += seconds

        with self.assertRaisesRegex(RuntimeError, "request failed"):
            verifier.verify("2.0.3", timeout=100, check=check,
                            sleep=sleep, clock=lambda: elapsed[0])
        self.assertEqual(elapsed[0], 120)

    def test_failed_verification_does_not_write_success_output(self):
        with patch.object(verifier.Path, "read_text", return_value="2.0.3"), \
                patch.dict(verifier.os.environ, {"GITHUB_OUTPUT": "unused", "RELEASE_TAG": "v2.0.3"}), \
                patch.object(verifier, "verify", side_effect=RuntimeError("unavailable")), \
                patch("builtins.open") as output:
            with self.assertRaises(RuntimeError):
                verifier.main()
            output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
