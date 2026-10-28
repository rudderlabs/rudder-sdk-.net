# Published .NET SDK acceptance

The published-package workflow runs the full central E2E suite for the exact stable release version. The publishing ref gate rejects prerelease versions before Windows packaging or NuGet authentication. It uses the existing release App and waits for delivery validation and cleanup. The central workflow checks the release tag against the immutable event commit and `master` ancestry. It installs the exact public registry package and verifies native package metadata and integrity evidence.

Acceptance starts only after the existing publisher succeeds. Existing native build, security, and publication checks remain in place. Release-complete notifications, where configured, wait for published-package acceptance.

Full source-candidate E2E before publication is a separate rollout. Do not treat native tests or this post-publication check as that gate.

Existing manual publication must select a release tag. A master-branch dispatch cannot bind the uploaded artifact to a release tag and is no longer a publication path.

## Validation-only retry

1. Open the failed central run from the shared action summary.
2. Resolve the validation failure.
3. Run this workflow at the existing release tag:

```sh
gh workflow run published-sdk-e2e.yml --repo rudderlabs/rudder-sdk-.net --ref vX.Y.Z
```

The retry has no upload path or publishing credential. It derives the exact version and commit from the selected tag. It does not use `latest`, publish a package, or recreate a tag. Tags predating this workflow need an exact-version dispatch through the central workflow. Stable `X.Y.Z` versions are supported; prerelease acceptance is not implemented.

A published package remains published if acceptance fails. The release-event Slack root reports "published; validation failed or incomplete" only after exact public NuGet verification. Earlier ref, pack, or upload failures report failed or unconfirmed publication, and a successful upload without public verification remains unconfirmed. Its non-broadcast thread reply links the NuGet version, release, and run with each job's result. Do not rerun a successful upload job to retry E2E. A successful validation-only retry does not change an earlier failed run or its notification. Record the new acceptance run in the release ticket and existing Slack release thread.

## Rollout

Tracked in [SDK-5969](https://linear.app/rudderstack/issue/SDK-5969). Keep this PR draft until [central PR #32](https://github.com/rudderlabs/rudder-sdk-e2e-tests/pull/32), including its committed cleanup-budget fix `52f6bf7`, and [SDK-5977](https://linear.app/rudderstack/issue/SDK-5977)'s shared workflow are reviewed and available. [SDK-5978](https://linear.app/rudderstack/issue/SDK-5978) does not make normal trusted inheritance an automatic blocker. Adopt the shared workflow only at a reviewed immutable ref. The current action pin is an existing commit from [shared-action PR #5](https://github.com/rudderlabs/github-action-sdk-e2e/pull/5) and must be verified or refreshed before merge. Hosted acceptance remains pending the next normal release. Do not create a release solely to test this wiring.
