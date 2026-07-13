# HealthSynth

> Learn pharmaceutical commercial analytics by generating realistic synthetic markets.

HealthSynth is an open-source Python framework that simulates pharmaceutical commercial markets and generates internally consistent synthetic datasets for analytics, experimentation, and learning.

Unlike traditional synthetic data generators that create independent tables, HealthSynth models how commercial markets actually behave. Products compete for market share, promotional activity influences adoption, market demand changes over time, and prescriptions emerge from these upstream commercial dynamics.

The result is a realistic commercial ecosystem that can be explored using Python, SQL, DuckDB, BI tools, or AI applications.

---

## Why HealthSynth?

Many excellent tools already exist for generating synthetic patients, electronic health records, and claims data.

HealthSynth addresses a different problem.

Commercial analytics teams ask questions such as:

- How does a new product launch affect market share?
- What happens when a leading brand loses exclusivity?
- How does increased promotional activity influence adoption?
- What is the impact of improved market access?
- Can a product lose market share while still growing prescriptions?

Answering these questions requires datasets that evolve together—not isolated synthetic tables.

HealthSynth simulates these commercial relationships so that every generated dataset remains connected to the others.

---

## What Makes HealthSynth Different?

HealthSynth is designed as a **commercial simulation framework**, not simply a synthetic data generator.

| Traditional Synthetic Data | HealthSynth |
|----------------------------|-------------|
| Generates independent datasets | Simulates connected commercial systems |
| Focuses on realistic records | Focuses on realistic commercial behaviour |
| Static relationships | Relationships evolve over time |
| Limited business context | Commercial events drive market dynamics |
| Primarily for testing | Designed for learning, experimentation and analytics |

---

## Commercial Simulation Flow

```text
Configuration
        │
        ▼
Commercial World
        │
        ├── Markets
        ├── Products
        ├── Healthcare Providers
        ├── Promotional Activity
        ├── Market Demand
        ├── Market Share
        └── Prescription Allocation
                │
                ▼
Synthetic Commercial Analytics Datasets
```

Every downstream dataset is produced from the commercial dynamics above rather than being generated independently.

---

## Current Capabilities

### Commercial Entities

- Markets
- Healthcare Providers (HCPs)
- Product portfolio
- Sales territories

### Commercial Dynamics

- Promotional call activity
- Promotion effect modelling
- Market demand simulation
- Dynamic market share
- Prescription allocation

### Commercial Events

- New Product Launch
- Loss of Exclusivity (LOE)
- Competitor Launch
- Market Access Improvement

### Outputs

- CSV datasets
- DuckDB database
- Dataset manifest
- Validation report

### Configuration

- YAML-based market profiles
- Configurable simulation parameters
- Reproducible simulations

---

## Generated Datasets

A typical simulation generates:

- `market`
- `hcp_master`
- `product`
- `call_activity`
- `promotion_effect`
- `market_demand`
- `market_share`
- `prescriptions`

All datasets are internally consistent and designed to work together.

---

## Quick Start

### Install

```bash
pip install healthsynth
```

### Generate a market

```bash
healthsynth generate \
    --config configs/profiles/oncology_training.yaml \
    --hcps 1000 \
    --output-dir output/demo
```

The simulation produces:

- CSV files
- DuckDB database
- Dataset manifest
- Validation report

---

## Learn HealthSynth

HealthSynth includes a notebook series that introduces both the framework and common pharmaceutical commercial analytics concepts.

1. Running HealthSynth
2. Market Profiles
3. Product Portfolio
4. Exploring Data with DuckDB
5. Market Share Analysis
6. Market Demand and Growth
7. New Product Launch
8. Loss of Exclusivity
9. Competitor Launch
10. Market Access

The notebooks are intended to teach both the framework and the commercial concepts behind the generated data.

---

## Who Is HealthSynth For?

HealthSynth is designed for:

- Data Engineers
- Data Scientists
- Analytics Engineers
- BI Developers
- SQL learners
- AI/LLM practitioners
- Students learning life sciences analytics
- Trainers delivering commercial analytics workshops

---

## Design Philosophy

HealthSynth was built around one simple principle:

> Commercial analytics should be learned using realistic commercial systems—not isolated synthetic tables.

Business assumptions belong in configuration.

Simulation logic belongs in code.

Generated datasets should reflect the commercial processes that produced them.

This makes it easier to understand not only *what* happened, but *why* it happened.

---

## Documentation

Additional documentation is available in the `docs` folder.

- Getting Started
- Data Model
- Architecture
- Learning Notebooks

---

## Roadmap

### Current Release

- End-to-end commercial simulation
- Commercial event modelling
- DuckDB integration
- Learning notebooks
- Validation framework

### Planned

- Additional therapeutic areas
- Omnichannel engagement scenarios
- Territory realignment
- AI-assisted scenario generation
- Performance optimisation
- Additional export formats

---

## Contributing

HealthSynth is an open-source project and contributions are welcome.

Whether you want to improve the simulation engine, documentation, notebooks, or add new commercial scenarios, contributions of all sizes are appreciated.

---

## License

MIT License

---

## Author

**Virendra Pratap Singh**

NVA Dataworks

LinkedIn:
https://www.linkedin.com/in/virendra-pratap-singh-iitg/