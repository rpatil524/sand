# Changelog

## [Unreleased]

### Added

- SAND Entity Editor UI, when users link new cell, it will automatically do an initial search using the cell as the query to save users time from re-entering the same information.
- SAND Entity Editor UI, we can apply search results to multiple cells at once.
- Users can export the linked entities
- Importing a dataset, if the readable labels are not available for nodes/edges in the semantic descriptions, users can generate a default one via `add-missing-readable-label` flag.

### Fixed

- Fix getting entity/class/property by id that has special characters such as /
- Handle querying external APIs returned unknown entities
- Fix exporting data as attachment cannot handle special characters in the filename

## [4.1.0] - 2024-04-13

### Added

- SAND CLI can import dataset returned from a python function

### Changed

- SAND CLI create project command does not require project's description (default to use dataset name)

## [Unreleased](https://github.com/usc-isi-i2/sand/tree/HEAD)

[Full Changelog](https://github.com/usc-isi-i2/sand/compare/2.1.5...HEAD)

### Changed

- Update dependency: `d-repr` version constraint to `^2.10.0` from prerelease version.
- Update dockerfile and add docker-compose example.

## [2.1.5](https://github.com/usc-isi-i2/sand/tree/2.1.5) (2022-06-23)
