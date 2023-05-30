# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 12.12.0 2023-05-30
### Added
* Tests for `add biosample` and `addempty biosample` behaviour when `anonymous_sample_id` is provided as `""`, or `None`.
* Tests for `add library` when biosamples are force created.

### Changed
* `addempty biosample` no longer automatically generates an `anonymous_sample_id` if one is not provided by a user.

### Fixed
* `add biosample` no longer allows reset of `anonymous_sample_id` by providing an empty string in `partial` mode.

## 12.11.0 2023-05-25
### Added 
* The `anonymous_sample_id` field, on the `BiosampleArtifact` model.
* Support for supplying the `anonymous_sample_id` to both `add biosample` and `addempty biosample` endpoints.
* Permissions `can_add_anonymous_sample_id` and `can_change_anonymous_sample_id` to control who can create their own ids, or change a pre-existing id (the latter should rarely be handed out, ideally never).
* Automatic generation of the `anonymous_sample_id` from `zana` if the id is not supplied by a user.
* Form validation of the `anonymous_sample_id` checking for prefix-postfix structure separated by a hyphen, acceptable prefixes, required postfix length, and alphanumeric characters only.
* Tests of both `add biosample` endpoint and `addempty biosample` endpoint functionality, in regards to the `anonymous_sample_id`.
* Updated `settings.py.example` with configuration options for this id.

## 12.10.0 2023-04-25
### Added
* `list_institutes` and `list_institutes_2` management commands for displaying institute opt in/out information.

### Changed
* `list_users` management command to display more user role information.

## 12.9.9 2022-03-07
### Fixed
* After two years of solid development, 1300 commits, 33 million API requests and over 2.5 million sequences, it's probably about time to give this thing a version number and CHANGELOG.
* To whom it may concern, take care of this application. She might have saved lives.
