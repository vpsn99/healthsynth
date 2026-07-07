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