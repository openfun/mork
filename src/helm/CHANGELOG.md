# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2024-12-03

### Added

- Add environment variables for Brevo configuration

### Changed

- Change Celery liveness and readiness probes to file-based probes
- Upgrade appVersion to `0.6.0`


## [0.5.1] - 2024-11-26

### Fixed

- Fix missing component label in Celery deployment

## [0.5.0] - 2024-11-25

### Added

- Add environment variables for Sentry configuration
- Add environment variables for deletion and emailing tasks configuration

### Changed

- Rename secret key reference for populating `MORK_EDX_MYSQL_DB_PASSWORD`
- Upgrade appVersion to `0.5.0`

### Fixed

- Narrow Celery deployment selector labels
- Add API component label to the migration job

## [0.4.0] - 2024-11-20

### Added

- Add environment variable `MORK_API_SERVER_HOST` that points to the API service

### Changed

- Upgrade appVersion to `0.4.0`

## [0.3.0] - 2024-11-04

### Changed

- Upgrade appVersion to `0.3.0`

## [0.2.0] - 2024-10-30

### Added

- Add configuration of Celery result backend transport options

### Changed

- Upgrade appVersion to `0.2.0`

## [0.1.0] - 2024-10-23

### Added

- Implement base Helm chart

[unreleased]: https://github.com/openfun/mork/tree/main/src/helm
[0.6.0]: https://github.com/openfun/mork/releases/tag/helm/v0.6.0
[0.5.1]: https://github.com/openfun/mork/releases/tag/helm/v0.5.1
[0.5.0]: https://github.com/openfun/mork/releases/tag/helm/v0.5.0
[0.4.0]: https://github.com/openfun/mork/releases/tag/helm/v0.4.0
[0.3.0]: https://github.com/openfun/mork/releases/tag/helm/v0.3.0
[0.2.0]: https://github.com/openfun/mork/releases/tag/helm/v0.2.0
[0.1.0]: https://github.com/openfun/mork/releases/tag/helm/v0.1.0
