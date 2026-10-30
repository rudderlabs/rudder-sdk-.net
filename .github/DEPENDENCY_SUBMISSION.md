# NuGet dependency submission

The workflow restores every SDK-style project with .NET SDK 8 on Windows, retaining every declared target framework. This includes the SDK, dependency-injection extension, tests and samples. The SDK's six target frameworks are unchanged; restore does not require running the old target runtimes.

Each restore must produce a nonempty `obj/project.assets.json` with all declared frameworks. The legacy `Test.Net35` project supplies `packages.config` as detector input. `Test.UniversalApp` uses `PackageReference` and has no `packages.config`. The workflow does not restore it, so its resolved dependencies are excluded from the claimed coverage until a compatible restore and detector path are validated.

Read-only jobs generate an artifact on pull requests, dependency changes on `master`, weekly refreshes and manual runs. A separate `contents: write` job consumes only the successful same-run artifact on `master`. It uses GitHub's recommended Component Detection submission action with only NuGet detection enabled. No project build runs in the submission job.

The pinned Component Detection action is on the organization allowlist as of 2026-10-30. Hosted restore, detector execution, and default-branch ingestion remain separate acceptance steps. After merge, inspect detector output and GitHub's actual graph. Confirm attribution to the covered projects, all SDK frameworks, direct/indirect packages and test/runtime scope handling. Check formerly omitted packages such as `System.Net.Primitives`. A nonempty graph alone does not establish full coverage.

Container contents and arbitrary downstream consumer resolutions remain separate. Existing Dependabot configuration and alert visibility are unchanged.

Rollback: remove this workflow. Previously submitted snapshots can remain until superseded or removed. Do not disable native alerts as a rollback step.
