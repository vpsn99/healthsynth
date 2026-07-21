# Changelog

All notable changes to HealthSynth will be documented in this file.

The format loosely follows Keep a Changelog.

---

## [Unreleased]

### Added

- Initial commercial analytics simulation engine
- HCP generation
- Product generation
- Call activity generation
- Prescription generation
- CLI interface
- CSV export

---

## [0.0.1] - 2026-07-07

Initial project foundation.

Features

- Python package
- Simulation architecture
- Commercial Analytics module
- New Product Launch scenario

## [0.1.0] - 2026-07-09

### Initial public release - Simulation engine.

### Added

- US Commercial market profile
- Scenario configuration framework
- Learning Path documentation
- Market entity as a first-class dataset
- Market metadata propagation across generated datasets
- Dataset manifest generation
- Project metadata module
- Profile-aware dataset generation

### Changed

- Manifest now includes market, generation parameters, timings and schema version.
- Product and HCP datasets now include market identifiers.


### Features

- Configuration-driven simulation
- Market demand
- Market share
- Prescription allocation
- DuckDB export
- CSV export
- Validation framework
- Commercial events
    - New Product Launch
    - LOE
    - Competitor Launch
    - Market Access
- Learning notebooks
- Documentation


### Added

- Initial commercial analytics simulation engine.
- YAML configuration.
- Multi-product simulation.
- Market demand modelling.
- Product launch scenario.
- Market access scenario.
- DuckDB export.
- Validation reports.
- Jupyter notebooks.
- 
## [0.2.0] - Unreleased

### Simulation engine + Studio + locality-aware generation + improved architecture.

### Added

- HealthSynth Studio interactive web application.
- Interactive timeline explorer for commercial scenarios.
- Narrative engine for scenario explanations.
- Locality-aware synthetic identity generation.
- Generic locality configuration supporting Faker locales.
- UK and Japan commercial market profiles.
- Address, postal code and phone number generation for HCPs.
- Country and locale metadata in generated datasets.

### Changed

- Refactored Studio into modular components.
- Generalized province into administrative_area.
- Expanded HCP schema with locality metadata.
- Updated output schema to version 2.0.
- Improved configuration validation.

### Fixed

- Improved deterministic generation across localized datasets.
- Improved configuration validation for unsupported Faker locales.

### Documentation

- Updated architecture documentation.
- Updated data model.
- Added locality configuration examples.
- Refreshed Getting Started guide.


Historical releases prior to 0.1.0 represent early development milestones
before HealthSynth reached its first public release.