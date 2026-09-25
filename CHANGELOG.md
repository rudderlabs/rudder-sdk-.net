#

## [2.0.3](https://github.com/rudderlabs/rudder-sdk-.net/compare/v2.0.2...v2.0.3) (2026-09-25)


### Bug Fixes

* sdk-5270 resolve nuget package path before publishing ([#48](https://github.com/rudderlabs/rudder-sdk-.net/issues/48)) ([ef1b5a2](https://github.com/rudderlabs/rudder-sdk-.net/commit/ef1b5a271bd211af9f84ce793848071f5e542428))


### Miscellaneous

* add Dependabot version-update config (SEC-359) ([#40](https://github.com/rudderlabs/rudder-sdk-.net/issues/40)) ([e7338b0](https://github.com/rudderlabs/rudder-sdk-.net/commit/e7338b029f1efb2461562e732900f03f28edbd5e))
* analyze master after merges ([#49](https://github.com/rudderlabs/rudder-sdk-.net/issues/49)) ([aa5ec3f](https://github.com/rudderlabs/rudder-sdk-.net/commit/aa5ec3f5018a38e30d18ceeb96163ab946f67170))
* migrate nuget publish to trusted publishing ([#33](https://github.com/rudderlabs/rudder-sdk-.net/issues/33)) ([bac8dc1](https://github.com/rudderlabs/rudder-sdk-.net/commit/bac8dc179c4ebd1a3f76a52d82932e415a9e4f90))
* sdk-5335 notify slack of github releases ([#41](https://github.com/rudderlabs/rudder-sdk-.net/issues/41)) ([65f7a92](https://github.com/rudderlabs/rudder-sdk-.net/commit/65f7a922025e44a90a83b6883499c8a68ba9cbc8))
* sdk-5339 decommission stale develop branch ([#43](https://github.com/rudderlabs/rudder-sdk-.net/issues/43)) ([2943fe4](https://github.com/rudderlabs/rudder-sdk-.net/commit/2943fe46388159d2a30516e17104d4d99573127c))
* switch branding images to CDN URLs ([#46](https://github.com/rudderlabs/rudder-sdk-.net/issues/46)) ([9389cbd](https://github.com/rudderlabs/rudder-sdk-.net/commit/9389cbdc0155ee31f6f9ed3f2a13cdd9a29fa44c))
* update branding icon and readme images ([#44](https://github.com/rudderlabs/rudder-sdk-.net/issues/44)) ([e0cd057](https://github.com/rudderlabs/rudder-sdk-.net/commit/e0cd0577d20d7971c33310328e08198ff17f7e7c))
* verify nuget publication before release notification ([#50](https://github.com/rudderlabs/rudder-sdk-.net/issues/50)) ([eababac](https://github.com/rudderlabs/rudder-sdk-.net/commit/eababac6f1c227dda62f09e80334fc894d4c12a5))


### Documentation

* sdk-5270 document the complete nuget release process ([#47](https://github.com/rudderlabs/rudder-sdk-.net/issues/47)) ([0f26c0b](https://github.com/rudderlabs/rudder-sdk-.net/commit/0f26c0b2a3b1498a17af3579cb7f1f9c98a5d931))

## [2.0.2](https://github.com/rudderlabs/rudder-sdk-.net/compare/v2.0.1...v2.0.2) (2026-07-20)


### Miscellaneous

* **codeowners:** set sdk_team as code owners ([#38](https://github.com/rudderlabs/rudder-sdk-.net/issues/38)) ([e430265](https://github.com/rudderlabs/rudder-sdk-.net/commit/e430265f5af5e0bf2f6343875b87bd838ba6bfd1))
* remove notion pr sync workflow ([61a0c0d](https://github.com/rudderlabs/rudder-sdk-.net/commit/61a0c0d1cbba2166d8b37936109ba779737b6ff5))
* remove notion pr sync workflow ([67bc4c6](https://github.com/rudderlabs/rudder-sdk-.net/commit/67bc4c6ef27b13bb6ea68dffb47dbf7a37f00ec1))
* sdk-4993 migrate dotnet sdk to release-please ([28c25ed](https://github.com/rudderlabs/rudder-sdk-.net/commit/28c25edd2849aaaa40a16781c59f1cb41deab230))
* sdk-4993 migrate dotnet sdk to release-please ([6120660](https://github.com/rudderlabs/rudder-sdk-.net/commit/6120660d0aa35740f4973880687e1ab93273908d))
* sdk-4993 update readme versions with release-please ([878135f](https://github.com/rudderlabs/rudder-sdk-.net/commit/878135faec61a66fc9e4004f5e8435880abb5a6a))

## [2.0.1](https://github.com/rudderlabs/rudder-sdk-.net/releases/tag/v2.0.1) (2026-05-15)

### Bug Fixes

- Resolved Snyk vulnerabilities in SDK dependencies (#28)
- Upgraded OSS dependencies with known vulnerabilities (#17)
- Fixed Snyk security issues in dependencies (#14)

## [2.0.0](https://github.com/rudderlabs/rudder-sdk-.net/releases/tag/v2.0.0) (2023-02-16)

### Breaking Changes

- Enabled the Gzip Compression Support by default

### Features

- Added a property channel, which is set to server in every event to indicate that this event is fired from server side SDK
- Added Support for .Net 5.0

## [1.0.1](https://github.com/rudderlabs/rudder-sdk-.net/releases/tag/v1.0.1) (2021-05-13)


### Bug Fixes

- Fixed the setup related issues
