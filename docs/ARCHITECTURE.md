# HealthSynth Architecture

HealthSynth is a configuration-driven simulation framework that models how pharmaceutical commercial markets evolve over time.

Rather than generating independent synthetic datasets, HealthSynth simulates the commercial relationships between markets, products, healthcare providers (HCPs), promotional activity, market demand, market share, and prescriptions.

The framework is designed around a simple principle:

> **Business assumptions belong in configuration. Simulation logic belongs in code.**

This separation allows the same simulation engine to create many different commercial environments simply by changing the configuration.

---

# Design Principles

HealthSynth was designed with five core principles.

## 1. Configuration Driven

Commercial assumptions should be defined in YAML rather than hard-coded.

Examples include:

- markets
- products
- HCP distribution
- channel mix
- market growth
- commercial events

Changing a market should not require changing Python code.

---

## 2. Commercial Relationships First

The goal is not to generate isolated tables.

Instead, HealthSynth models the relationships that exist inside a commercial organization.

For example:

```
Products
        │
Promotional Activity
        │
Market Demand
        │
Market Share
        │
Prescriptions
```

Every downstream dataset is influenced by upstream commercial dynamics.

---

## 3. Reproducible Simulations

Given the same configuration and random seed, HealthSynth should generate identical outputs.

This makes the framework suitable for:

- learning
- experimentation
- testing
- demonstrations

---

## 4. Explainable Simulation

Every generated value should be traceable back to the commercial assumptions that produced it.

For example:

```
Market Demand
        ×
Adjusted Market Share
        =
Product Demand
```

Rather than hiding simulation logic inside statistical models, HealthSynth aims to make each commercial step understandable.

---

## 5. Modular Design

Commercial concepts are implemented as independent components.

New commercial events should be added without rewriting the rest of the simulation engine.

---

# High-Level Architecture

The overall simulation pipeline is shown below.

```
                 YAML Configuration
                         │
                         ▼
             Configuration Validation
                         │
                         ▼
                Simulation Engine
                         │
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
   Markets           Products            HCP Master
                         │
                         ▼
               Commercial Activity
      ┌──────────────────┼──────────────────┐
      ▼                  ▼                  ▼
 Promotion         Market Demand      Market Share
                         │
                         ▼
              Prescription Allocation
                         │
                         ▼
     CSV • DuckDB • Validation • Manifest
```

Each stage produces data that is consumed by later stages.

---

# Simulation Pipeline

Every HealthSynth simulation follows the same sequence.

## Step 1 — Load Configuration

The selected YAML profile is loaded.

The profile defines:

- market
- products
- specialties
- promotional channels
- simulation duration
- commercial events

---

## Step 2 — Validate Configuration

Before simulation begins, HealthSynth validates:

- required fields
- probability distributions
- product definitions
- event configuration
- business rules

Invalid configurations are rejected before any data is generated.

---

## Step 3 — Generate Master Data

Master datasets establish the commercial world.

These include:

- markets
- products
- HCPs
- territories

These datasets change infrequently during the simulation.

---

## Step 4 — Generate Commercial Activity

HealthSynth generates promotional interactions between pharmaceutical products and healthcare providers.

Examples include:

- representative calls
- emails
- webinars
- conferences
- digital promotion

This activity becomes one input into later commercial dynamics.

---

## Step 5 — Simulate Market Demand

Market demand represents the total prescription opportunity available during each month.

Demand is influenced by:

- baseline market size
- growth
- seasonality

The result is a monthly market-level prescription target.

---

## Step 6 — Calculate Market Share

Products compete for the available demand.

Market share begins with configured assumptions and is modified by commercial dynamics including:

- promotional activity
- new product launch
- competitor launch
- loss of exclusivity
- market access
- controlled variation

The adjusted market share for every product is calculated monthly.

A key business rule is maintained:

```
Monthly Product Shares = 100%
```

---

## Step 7 — Allocate Prescriptions

Once market demand and adjusted market share are known, prescriptions are allocated.

Conceptually:

```
Market Demand
        ×
Adjusted Market Share
        =
Product Demand
```

Product demand is then distributed across individual healthcare providers.

The allocation process preserves the total market demand while ensuring prescription counts remain whole numbers.

---

## Step 8 — Export Results

Generated datasets are exported as:

- CSV files
- DuckDB database

Additional outputs include:

- validation report
- dataset manifest

---

# Core Components

HealthSynth is organised around several independent simulation components.

| Component | Responsibility |
|-----------|----------------|
| Configuration | Load and validate market profiles |
| Market Generator | Create market definitions |
| Product Generator | Create product portfolio |
| HCP Generator | Generate healthcare providers |
| Call Activity Generator | Simulate promotional interactions |
| Promotion Engine | Estimate promotional influence |
| Market Demand Engine | Calculate monthly prescription opportunity |
| Market Share Engine | Allocate competitive market share |
| Prescription Generator | Allocate product prescriptions |
| Export Layer | CSV and DuckDB output |
| Validation Engine | Verify business consistency |

Each component has a single responsibility and communicates through generated datasets.

---

# Commercial Events

HealthSynth supports commercial events that modify market behaviour without changing the simulation pipeline.

Current event types include:

- New Product Launch
- Loss of Exclusivity (LOE)
- Competitor Launch
- Market Access Improvement

Each event influences market share before prescription allocation occurs.

This allows multiple events to interact while keeping the simulation architecture consistent.

---

# Data Flow

The major datasets produced during the simulation are connected.

```
Market
      │
      ▼
Products ───────────────┐
      │                 │
      ▼                 │
Call Activity           │
      │                 │
      ▼                 │
Promotion Effect        │
      │                 │
      ▼                 │
Market Share ◄──────────┘
      │
      ▼
Market Demand
      │
      ▼
Prescriptions
```

Each dataset contributes to later stages of the simulation.

---

# Validation

HealthSynth validates generated outputs before completing a simulation.

Examples include:

- market share sums to 100%
- prescription totals reconcile with market demand
- product references remain valid
- configuration rules are satisfied

Validation reports are generated automatically.

---

# Extension Points

HealthSynth is designed to be extended.

Examples include:

- additional commercial events
- new promotional channels
- new therapeutic areas
- additional output formats
- country-specific market profiles
- alternative market share models

Most extensions require configuration changes and isolated simulation components rather than changes across the entire codebase.

---

# Project Structure

```
healthsynth/
│
├── config/
├── generators/
├── simulation/
├── exports/
├── validation/
├── cli/
├── examples/
├── docs/
├── tests/
└── configs/
```

The project separates configuration, simulation logic, export, validation, and documentation into independent modules.

---

# Architecture Summary

HealthSynth is built around one central idea:

```
Business Assumptions
        │
Configuration
        │
Commercial Simulation
        │
Internally Consistent Data
        │
Analytics & Learning
```

Rather than generating disconnected synthetic datasets, HealthSynth simulates the commercial processes that produce those datasets.

This architecture allows users to experiment with realistic pharmaceutical commercial scenarios while maintaining consistency across every generated output.