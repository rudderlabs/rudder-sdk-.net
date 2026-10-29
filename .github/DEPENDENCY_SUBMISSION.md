# NuGet dependency submission

The workflow restores every SDK-style project with .NET SDK 8 on Windows, retaining every declared target framework. This includes the SDK, dependency-injection extension, tests and samples. The SDK's six target frameworks are unchanged; restore does not require running the old target runtimes.

Each restore must produce a nonempty `obj/project.assets.json` with all declared frameworks. The two legacy projects, `Test.Net35` and `Test.UniversalApp`, retain their `packages.config` inventory; this workflow does not claim a modern restore/build of those projects.

Read-only jobs generate an artifact on pull requests, dependency changes on `master`, weekly refreshes and manual runs. A separate `contents: write` job consumes only the successful same-run artifact on `master`. It uses GitHub's recommended Component Detection submission action with only NuGet detection enabled. No project build runs in the submission job.

The new immutable Component Detection and download-artifact pins require allowlist verification before hosted acceptance. After merge, inspect detector output and GitHub's actual graph. Confirm attribution to all projects, all SDK frameworks, direct/indirect packages and test/runtime scope handling. Check formerly omitted packages such as `System.Net.Primitives`. A nonempty graph alone does not establish full coverage.

Container contents and arbitrary downstream consumer resolutions remain separate. Existing Dependabot configuration and alert visibility are unchanged.

Rollback: remove this workflow. Previously submitted snapshots can remain until superseded or removed. Do not disable native alerts as a rollback step.
