# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fix incorrect status code check when deleting user contact

### Removed

- Remove uniqueness constraint on username field

## [0.9.0] - 2025-03-17

### Changed

- Migrate from Brevo to Sarbacane

## [0.8.0] - 2025-01-22

### Fixed

- Fix ASCII encoding issue for email containing non-ASCII characters
- Fix edX `auth_user_groups` relation 
- Fix edX `student_manualenrollmentaudit` relation

### Removed

- Remove email validation for emails coming from edx

## [0.7.0] - 2024-12-16

### Changed

- Disable Brevo request on empty Brevo API URL setting
- Activate recursive scrubbing of Sentry events
- Silently exit brevo task for already deleted users

### Fixed

- Remove user email from Brevo request breadcrumb before sending to Sentry

## [0.6.0] - 2024-12-02

### Added

- Add and protect `wiki_article` and `wiki_articlerevision` tables
- Add `created_at` and `updated_at` fields to response from user API
- Add custom liveness and readiness probe for Celery
- Add `PROTECTED` status to user deletion workflow
- Add task to delete contacts from Brevo

### Fixed

- Scrub `email` and `username` fields from logs and exceptions sent to Sentry
- Catch errors from the database driver

## [0.5.0] - 2024-11-25

### Added

- Add edx mongodb task to anonymize personal data from edx forums
- Add Sentry configuration for Celery

### Changed

- Improve task status endpoint path to `tasks/task_id/status`

### Fixed

- Correct email templates path in Dockerfile
- Ensure API status updates are committed to database

## [0.4.0] - 2024-11-20

### Added

- Add `users` endpoints for services to retrieve the list of users to delete
- Flag users for deletion in Mork database when deletion process begins
- Add status verification checks before and after user deletion in edX
- Add support for emailing a single user via api
- Add an optional `limit` parameter for bulk deletion and warning tasks

### Changed

- Add a dry-run parameter to the task creation API (defaults to True)
- Introduce API versioning with `v1` namespace

### Fixed

- Fix HTTP 500 errors on heartbeat endpoint when QueuePool limits are reached

## [0.3.0] - 2024-11-04

### Added

- Allow to OPTIONS and POST `tasks` endpoint without a trailing slash

### Fixed

- Remove unused `REDIS_` environment variables that cause conflict on k8s

## [0.2.0] - 2024-10-30

### Added

- Add configuration for Celery result backend transport options

### Fixed

- Fix relations in student_manualenrollmentaudit table for cascade delete

## [0.1.0] - 2024-10-22

#### Added

- Bootstrap base backend boilerplate
- Implement tasks endpoints
- Add connection to edx database to read user table
- Implement user data deletion method on edx database
- Add celery task to warn inactive users by email
- Add celery task to delete inactive users from edx database

[unreleased]: https://github.com/openfun/mork/compare/v0.9.0...main
[0.9.0]: https://github.com/openfun/mork/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/openfun/mork/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/openfun/mork/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/openfun/mork/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/openfun/mork/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/openfun/mork/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/openfun/mork/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openfun/mork/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/openfun/mork/compare/1e60ac8...v0.1.0
