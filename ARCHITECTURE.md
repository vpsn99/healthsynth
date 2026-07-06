# HealthSynth Architecture

HealthSynth is organized around the idea of simulation rather than data generation.

Instead of creating disconnected tables, HealthSynth simulates a commercial healthcare environment.

---

# High-Level Architecture

```
Commercial Simulation
        │
        ▼
    Entities
        │
        ▼
     Events
        │
        ▼
      Facts
        │
        ▼
    Exporters
```

---

# Entities

Entities are things that exist.

Examples:

- HCP
- Product
- Territory
- Sales Representative

Entities change slowly and form the foundation of the simulation.

---

# Events

Events are things that happen.

Examples:

- Rep Call
- Sample Drop
- Product Launch
- Campaign
- Territory Realignment

Events drive business behaviour.

---

# Facts

Facts measure business outcomes.

Examples:

- Prescriptions
- Sales
- Engagement
- Utilization

Facts should emerge naturally from entities and events.

---

# Exporters

The simulation engine is independent of storage.

Exporters convert generated datasets into different formats.

Current:

- CSV

Planned:

- DuckDB
- Parquet
- SQL
- dbt
- Snowflake
- Fabric

---

# Modules

Each healthcare domain is implemented as an independent module.

Examples:

- Commercial Analytics
- Claims Analytics
- Provider Analytics
- Clinical Trials

Modules should share common simulation infrastructure while remaining independently extensible.

---

# Scenarios

Scenarios modify business behaviour.

Examples:

- New Product Launch
- Loss of Exclusivity
- Territory Realignment
- Digital First Campaign

Scenarios should influence events.

Events should influence facts.

Scenarios should never directly manipulate output tables.

---

# Design Principles

HealthSynth prefers:

- simulation over random generation
- explicit business rules
- deterministic outputs
- configurable behaviour
- modular architecture
- clean separation between simulation and export