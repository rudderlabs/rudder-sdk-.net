# Releasing the .NET SDK

This file is the source of truth for the release workflow and recovery commands.
The [Notion release guide](https://app.notion.com/p/a70171eea93b491ea47b32e38be9ef26)
provides the team runbook and current validation record. It is linked from the
[.NET SDK hub](https://app.notion.com/p/38bf2b415dd08173bafef21355856d5e).

Release Please manages versions, the changelog, tags, and GitHub releases on
`master`. The separate [Publish NuGet Package workflow](.github/workflows/publish-nuget.yml)
builds and publishes `RudderAnalytics` when a GitHub release is published.

## Configure publishing before merging a release PR

1. Sign in to [NuGet](https://www.nuget.org/users/account/LogOn) with the SDK team's
   Microsoft account. Use the current Microsoft Entra credentials referenced in
   the Notion guide and complete MFA when requested.
2. Confirm that the signed-in NuGet user can administer the `rudderlabs` owner
   and the `RudderAnalytics` package. The NuGet profile username can differ from
   the Microsoft email address and the package owner name.
3. Check the user's NuGet Trusted Publishing policy against the following values.

   | Setting | Value |
   | --- | --- |
   | Package owner | `rudderlabs` |
   | Package scope | `RudderAnalytics` only |
   | Permission | Push new versions of the existing package |
   | GitHub repository owner | `rudderlabs` |
   | GitHub repository | `rudder-sdk-.net` |
   | Workflow file | `publish-nuget.yml` (filename only) |
   | GitHub environment | `release` |

4. Confirm that the policy is active. If NuGet shows a temporary activation
   window, complete validation before that window expires.
5. Confirm that the GitHub `release` environment permits the `master` branch and
   `v*` tags. Retain any configured reviewer requirements.
6. Set the environment secret `NUGET_USER` to the NuGet profile username that owns
   the policy and has the required package-owner access. Do not substitute the
   email address or organization name unless it is also the actual username.

The publish job uses OpenID Connect (OIDC) to exchange a GitHub identity token for
a short-lived NuGet API key. It does not read a stored `NUGET_API_KEY` secret.
See [NuGet Trusted Publishing](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing).

## Release procedure

1. Merge the intended changes into `master`.
2. Wait for [Release Please](.github/workflows/release-please.yml) to update the
   generated `chore: release X.Y.Z` pull request.
3. Review the changelog and the generated versions in `VERSION`,
   `.release-please-manifest.json`, `README.md`,
   `RudderAnalytics/RudderAnalytics.cs`, and `RudderAnalytics/RudderAnalytics.csproj`.
4. Confirm the publishing prerequisites above, required checks, and required
   reviews before merging the release PR.
5. Merge the release PR. Release Please creates the `vX.Y.Z` tag and GitHub
   release. Do not create duplicate tags or releases manually.
6. Open the resulting `Publish NuGet Package` run and confirm it uses the intended
   release commit. Complete any configured environment approval.
7. Verify the new NuGet package with the checks below.

The workflow validates the ref, restores/builds/packs on Windows, transfers the
package artifact to the publish job, authenticates to NuGet, and pushes the package.
Only the publish job receives `id-token: write` permission.

The Slack `#releases` notification announces creation of the **GitHub release**.
It can arrive before NuGet publication finishes. It is not proof that a package
was published. Check both the publishing run and NuGet.

Tag pushes alone do not start the publishing workflow. Release Please uses a
GitHub App token so its published-release event can start downstream workflows.

## Verify the published package

1. Inspect the publish logs for a successful upload of the expected package and
   version. A green run that only skipped an existing version is not a new
   publication.
2. Wait for NuGet indexing and signing. Confirm the version on the
   [RudderAnalytics package page](https://www.nuget.org/packages/RudderAnalytics)
   and in the [version index](https://api.nuget.org/v3-flatcontainer/rudderanalytics/index.json).
3. Download the published `.nupkg`, then run `dotnet nuget verify` on that file.
4. Restore and build a clean consumer project from the official NuGet source.

Example for a POSIX shell with .NET SDK 8 installed. Replace `X.Y.Z` with the
released version. A separate package cache prevents a local package from hiding
a publication or restore problem.

```sh
release_version=X.Y.Z
release_check_dir=$(mktemp -d)
curl --fail --location \
  "https://api.nuget.org/v3-flatcontainer/rudderanalytics/$release_version/rudderanalytics.$release_version.nupkg" \
  --output "$release_check_dir/RudderAnalytics.$release_version.nupkg"
dotnet nuget verify "$release_check_dir/RudderAnalytics.$release_version.nupkg" --all
dotnet new console --framework net8.0 --output "$release_check_dir/consumer"
dotnet add "$release_check_dir/consumer" package RudderAnalytics \
  --version "$release_version" --no-restore
dotnet restore "$release_check_dir/consumer" \
  --source https://api.nuget.org/v3/index.json \
  --packages "$release_check_dir/packages"
dotnet build "$release_check_dir/consumer" --no-restore
```

Record the release tag, successful workflow run, NuGet version, signature result,
and consumer build result in the release ticket. This consumer check does not
replace the repository's tests for all supported target frameworks.

## Recovery

- **Authentication fails:** check `NUGET_USER`, policy ownership, activation,
  package scope, workflow filename, and environment. Fix the configuration, then
  rerun the failed publishing job. The new attempt obtains a fresh short-lived key.
- **No publishing run exists:** check the Release Please run and its GitHub App
  credentials. Publishing requires a published-release event, not a tag push.
- **Manual recovery is needed:** dispatch the existing workflow against the
  intended release tag. The tag must contain `publish-nuget.yml`. Prefer rerunning
  the original release run when it exists.

  ```sh
  gh workflow run publish-nuget.yml \
    --repo rudderlabs/rudder-sdk-.net --ref vX.Y.Z
  ```

  The workflow also permits dispatch from `master`. This builds the version
  currently on that branch, which may already exist on NuGet. It must not be
  mistaken for a new release or a full publishing test when `--skip-duplicate`
  skips the upload. Tags created before the workflow was added cannot run it.

- **A version already exists:** inspect the existing package. NuGet versions
  cannot be overwritten. Publish a new patch version for package defects; do not
  delete or recreate release tags as a repair.

### Emergency manual publishing

Use this only when the normal publishing workflow cannot be recovered and the
release owner has approved manual publication of the intended release commit.

Use an unexpired, package-scoped key from the team's 1Password vault. Check its
actual expiration and permissions before use. The temporary key created for the
August 2026 release is not evidence that a valid key is still available.
Never commit a key or paste its value into documentation, tickets, or logs.

Build from a clean checkout of the intended release tag, with the reference packs
needed for every target framework. The publishing workflow uses Windows; use an
equivalent build environment for the complete package.

```sh
dotnet restore RudderAnalytics/RudderAnalytics.csproj
dotnet build RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-restore
dotnet pack RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-build --output artifacts
```

Inject the key into the process environment from 1Password without writing its
literal value into shell history. With shell tracing disabled, publish using:

```sh
dotnet nuget push artifacts/RudderAnalytics.X.Y.Z.nupkg \
  --source https://api.nuget.org/v3/index.json --api-key "$NUGET_API_KEY"
unset NUGET_API_KEY
```

Run the same published-package checks after manual publication. Retire a retained
legacy key only after a successful Trusted Publishing release is verified and the
release owner confirms that the fallback is no longer required.
