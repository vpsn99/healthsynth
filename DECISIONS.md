# HealthSynth Design Decisions

This document records important architectural and product decisions made during the evolution of HealthSynth.

The goal is to preserve the reasoning behind decisions so they do not need to be rediscovered later.

---

## HS-001

### Title

Commercial Analytics as the First Module

### Status

Accepted

### Date

2026-07-06

### Decision

HealthSynth will begin with the Commercial Analytics module.

### Reasoning

Clinical synthetic data already has mature open-source projects such as Synthea.

Commercial healthcare analytics remains largely underserved despite being widely used inside pharmaceutical organizations.

Starting here provides stronger differentiation and aligns with the project's target audience.

### Consequences

Initial development focuses exclusively on:

- HCPs
- Products
- Rep Calls
- Prescriptions

Claims, Clinical Trials and Provider Analytics become future modules.

---

## HS-002

### Title

Simulation Engine instead of Data Generator

### Status

Accepted

### Date

2026-07-06

### Decision

HealthSynth is implemented as a simulation engine rather than a collection of random table generators.

### Reasoning

Business events should produce data.

Not the other way around.

Scenarios become much easier to model when events drive downstream facts.

### Consequences

Architecture evolves around:

World

↓

Entities

↓

Events

↓

Facts

↓

Exporters

---

## HS-003

### Title

Business Realism over Statistical Realism

### Status

Accepted

### Decision

HealthSynth prioritizes believable business behaviour rather than statistically perfect healthcare populations.

### Reasoning

The primary audience is learning analytics engineering and data platforms.

Relationships between entities are more valuable than perfectly matching national healthcare statistics.

### Consequences

Examples include:

- Calls influence prescriptions.
- Launches change adoption.
- Territory changes affect activity.

---

## HS-004

### Title

Go Deep Before Wide

### Status

Accepted

### Decision

HealthSynth will build one realistic module before expanding into additional healthcare domains.

### Reasoning

A small believable simulation is more valuable than many shallow datasets.

### Consequences

Commercial Analytics reaches maturity before Claims or Provider Analytics begin.

---

## HS-005

### Title

Monthly Prescription Grain

### Status

Accepted

### Decision

Prescription facts are generated monthly in the initial releases.

### Reasoning

Monthly grain is sufficient for SQL, BI, warehouse, and ML demonstrations while keeping datasets compact.

### Future Considerations

Weekly and daily grain remain possible extensions.

---

## HS-006

### Title

Deterministic Generation

### Status

Accepted

### Decision

Every generation must be reproducible using a seed.

### Reasoning

Tutorials, unit tests and debugging all depend on deterministic behaviour.

### Consequences

Every generator accepts a seed parameter.

---

## HS-007

### Title

Scenario-Driven Simulation

### Status

Accepted

### Decision

Scenarios influence business events rather than directly modifying output tables.

### Reasoning

This better represents real business processes and keeps simulation logic modular.

### Example

Product Launch

↓

More Calls

↓

Higher Adoption

↓

More Prescriptions

Not:

Product Launch

↓

Increase prescriptions by 20%

---

## HS-008

### Title

Keep the First Public Release Small

### Status

Accepted

### Decision

The first public release intentionally supports only one scenario and one module.

### Reasoning

Quality, documentation and trust are more important than feature count during the early stages of the project.

### Consequences

The MVP contains:

- Commercial Analytics
- New Product Launch
- CSV
- DuckDB


## HS-009

### Title

Use Diminishing Returns for Call Response

### Status

Accepted

### Date

2026-07-07

### Decision

HealthSynth will model the impact of rep calls on prescriptions using a diminishing returns function.

The initial implementation uses `log1p(lagged_calls)`.

### Reasoning

A linear relationship between calls and prescriptions is unrealistic.

In commercial analytics, additional promotional activity usually has a saturation effect: the first few calls may matter, but each additional call contributes less incremental lift.

### Consequences

The initial model is simple and explainable.

Future versions may support configurable response functions such as:

- linear
- square root
- logarithmic
- Hill curve

## HS-010

### Title

Seasonality Should Be Configurable Over Time

### Status

Accepted

### Date

2026-07-07

### Decision

HealthSynth will include simple seasonality in the commercial analytics simulation.

The initial implementation treats July, August, and December as lower-activity months.

### Reasoning

Commercial healthcare activity is affected by holidays, vacations, and business calendars.

Seasonality makes generated data more useful for analytics, dashboards, and time-series exploration.

### Consequences

The current implementation is intentionally simple.

Future versions should move seasonality into configuration so users can simulate different markets and business calendars.

## HS-011

### Title

Support Multiple Products in Commercial Analytics Simulation

### Status

Accepted

### Date

2026-07-08

### Decision

HealthSynth will support multiple products within the Commercial Analytics module.

The initial implementation includes:

- P001 - CardioOne
- P002 - NeuroMax
- P003 - EndoCare

Products include metadata such as:

- product_id
- product_name
- therapeutic_area
- launch_date
- market
- status

### Reasoning

Real commercial analytics environments almost always involve multiple products.

Supporting multiple products enables:

- market share analysis
- brand performance reporting
- product-level dashboards
- future competitor simulations
- loss of exclusivity scenarios
- campaign analytics
- next best action use cases

### Consequences

Prescription generation is now performed at:

HCP × Month × Product

rather than:

HCP × Month

This increases dataset size but substantially improves realism and analytical usefulness.

Future versions may support:

- competitor products
- generic products
- product hierarchies
- multi-market product catalogs
- YAML-based product configuration

## HS-012

### Title

Model Specialty-Product Affinity

### Status

Accepted

### Date

2026-07-08

### Decision

HealthSynth will model product prescribing behavior using specialty-product affinity.

Each specialty has a configurable affinity toward products.

Examples:

- Cardiology → CardioOne
- Neurology → NeuroMax
- Endocrinology → EndoCare

Primary Care maintains affinity across multiple products.

### Reasoning

In real pharmaceutical markets, products are not prescribed equally across specialties.

Modeling affinity creates:

- more believable prescription patterns
- meaningful product segmentation
- realistic dashboard behavior
- foundations for market share and campaign analytics

### Consequences

Affinity values are currently stored in application configuration.

Future versions may support:

- YAML-based affinity configuration
- market-specific affinity models
- competitor affinity
- physician preference modeling
- switching behavior between products

## HS-013

### Title

Configuration is a First-Class Architectural Component

### Status

Accepted

### Date

2026-07-08

### Decision

HealthSynth separates configuration logic from simulation logic.

Configuration is loaded through a dedicated ConfigLoader that merges application defaults with optional YAML overrides.

Simulation components consume the merged configuration rather than reading defaults directly.

### Reasoning

This separation keeps business knowledge independent from the simulation engine.

It enables:

- configurable markets
- configurable products
- configurable channels
- configurable scenarios
- future module expansion

without changing generator implementations.

### Consequences

The configuration layer becomes part of the public architecture of HealthSynth rather than an implementation detail.

## HS-014

### Title

Business Knowledge Lives in Configuration

### Status

Accepted

### Date

2026-07-08

### Decision

HealthSynth will gradually move commercial business knowledge from Python code into YAML configuration.

Examples include:

- products
- specialty distributions
- channel distributions
- seasonality
- affinity mappings
- market templates

### Reasoning

Healthcare subject matter experts should be able to improve realism without modifying Python code.

The simulation engine should execute business rules rather than contain them.

### Consequences

Future releases will introduce configuration packs for markets and scenarios.

Python becomes the simulation engine.

YAML becomes the knowledge layer.

## Emerging Design Principle

HealthSynth should expose a simple data generation interface while internally using simulation principles to create believable business behavior.

Public identity:
Data Generator

Internal architecture:
Simulation Engine