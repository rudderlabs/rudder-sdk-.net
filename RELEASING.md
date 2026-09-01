# Releasing

Prerequisites:

- Install the .NET SDK from https://dotnet.microsoft.com/en-us/download/dotnet.
- Confirm the `RudderAnalytics` package owner has a NuGet Trusted Publishing policy for this repository.
- Configure the GitHub `release` environment with `NUGET_USER` as a repository/environment secret containing the NuGet.org username of an administrator of the `rudderlabs` organization. Do not use the organization name.

## NuGet Trusted Publishing setup

NuGet publishing uses GitHub Actions OIDC instead of a long-lived `NUGET_API_KEY`. The NuGet.org Trusted Publishing policy for `RudderAnalytics` must match:

- Repository Owner: `rudderlabs`
- Repository: `rudder-sdk-.net`
- Workflow File: `publish-nuget.yml`
- Environment: `release`

Keep the legacy `NUGET_API_KEY` secret until one Trusted Publishing release succeeds. After that release is verified on NuGet.org, remove or rotate the old API key secret.

## NuGet publish flow

Publishing is handled by the `Publish NuGet Package` workflow when a GitHub release is published. Tag push events do not publish packages.

Before publishing a release, verify the package locally:

```sh
dotnet restore RudderAnalytics/RudderAnalytics.csproj
dotnet build RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-restore
dotnet pack RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-build --output artifacts
```

Publish the GitHub release for the intended `vX.Y.Z` tag after the release changes are on `master`. Confirm the workflow completes successfully and the `RudderAnalytics` version appears on NuGet.org.

The publish workflow can also be started manually with `workflow_dispatch`, but only from a tag or the `master` branch.
