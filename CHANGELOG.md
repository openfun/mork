# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Fixed

- Fix relations in student_manualenrollmentaudit table for cascade delete

## [0.1.0] - 2024-10-22

### Added

- Bootstrap base backend boilerplate
- Implement tasks endpoints
- Add connection to edx database to read user table
- Implement user data deletion method on edx database
- Add celery task to warn inactive users by email
- Add celery task to delete inactive users from edx database

[unreleased]: https://github.com/openfun/mork/compare/v0.1.0...main
[0.1.0]: https://github.com/openfun/mork/compare/1e60ac8...v0.1.0
