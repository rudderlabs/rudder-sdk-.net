# Releasing

Prerequisites:

- Install the .NET SDK from https://dotnet.microsoft.com/en-us/download/dotnet.
- Confirm the `RudderAnalytics` package owner has a NuGet Trusted Publishing policy for this repository.
- Configure the GitHub `release` environment with `NUGET_USER` as a repository/environment variable or secret matching the NuGet.org user or organization profile name.

## NuGet Trusted Publishing setup

NuGet publishing uses GitHub Actions OIDC instead of a long-lived `NUGET_API_KEY`. The NuGet.org Trusted Publishing policy for `RudderAnalytics` must match:

- Repository Owner: `rudderlabs`
- Repository: `rudder-sdk-.net`
- Workflow File: `publish-nuget.yml`
- Environment: `release`

Keep the legacy `NUGET_API_KEY` secret until one Trusted Publishing release succeeds. After that release is verified on NuGet.org, remove or rotate the old API key secret.

## Release steps

1. Change the version in `RudderAnalytics/RudderAnalytics.csproj` (`Version` and `ReleaseVersion`).
2. Update the version in `RudderAnalytics/RudderAnalytics.cs`.
3. Update the latest version and install snippet in `README.md`.
4. Verify the package locally:
   `dotnet restore RudderAnalytics/RudderAnalytics.csproj`
   `dotnet build RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-restore`
   `dotnet pack RudderAnalytics/RudderAnalytics.csproj --configuration Release --no-build --output artifacts`
5. Commit the release changes: `git commit -am "Release X.Y.Z."`.
6. Tag the release: `git tag -a vX.Y.Z -m "Version X.Y.Z"`.
7. Push the release commit: `git push origin master`.
8. Push the release tag: `git push origin vX.Y.Z`.
9. Confirm the `Publish NuGet Package` workflow completes successfully and publishes `RudderAnalytics` to NuGet.org.
10. Create a GitHub release from the pushed tag at https://github.com/rudderlabs/rudder-sdk-.net/tags.

The publish workflow can also be started manually with `workflow_dispatch` after the release commit is present on the branch or tag to publish.
