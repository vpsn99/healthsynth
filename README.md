# HealthSynth

> An open-source commercial analytics simulation framework for life sciences.

HealthSynth simulates realistic pharmaceutical commercial markets and generates synthetic datasets that reflect how commercial dynamics evolve over time.

Rather than generating isolated tables independently, HealthSynth models the relationships between markets, products, healthcare providers (HCPs), promotional activity, market share, and prescription demand, producing internally consistent datasets suitable for learning, analytics, and experimentation.

---

## Why HealthSynth?

Most synthetic healthcare datasets focus on patients or clinical records.

HealthSynth focuses on **commercial analytics**.

It simulates how pharmaceutical markets behave by modelling:

- Markets
- Healthcare providers (HCPs)
- Products
- Territories
- Promotional activity
- Market demand
- Market share
- Prescription allocation

The generated prescription data is the result of these upstream commercial dynamics rather than being generated independently.

---

## Commercial Simulation Flow

```
Configuration
        │
        ▼
Commercial Simulation
        │
        ├── Markets
        ├── Products
        ├── HCPs
        ├── Promotional Activity
        ├── Market Demand
        ├── Market Share
        └── Prescription Allocation
                │
                ▼
Synthetic Commercial Analytics Datasets
```

---

## Current Features

HealthSynth currently generates:

- ✅ Market definitions
- ✅ Healthcare provider (HCP) master data
- ✅ Product portfolio
- ✅ Market demand simulation
- ✅ Promotional call activity
- ✅ Promotion effect modelling
- ✅ Dynamic market share
- ✅ Prescription allocation
- ✅ CSV export
- ✅ DuckDB export
- ✅ Dataset manifest
- ✅ Validation reports
- ✅ Configurable YAML profiles
- ✅ Learning notebooks

---

## Example Datasets

A typical simulation produces datasets including:

- `market`
- `hcp_master`
- `product`
- `market_demand`
- `call_activity`
- `promotion_effect`
- `market_share`
- `prescriptions`

---

## Design Philosophy

HealthSynth is designed as a learning sandbox for life sciences commercial analytics.

The project emphasizes:

- realistic commercial behaviour
- explainable simulation logic
- reproducible synthetic data
- clean, extensible architecture
- educational notebooks

Rather than simply generating synthetic records, HealthSynth models the commercial processes that produce those records.

---

## Current Status

HealthSynth is under active development.

The current release provides an end-to-end commercial simulation pipeline with configurable market profiles and internally consistent prescription generation.

Upcoming work includes:

- Commercial scenarios (New Product Launch, Loss of Exclusivity, Competitor Launch)
- Additional promotional channels
- Advanced market dynamics
- Expanded learning notebooks
- Performance optimization
- Additional export formats

---

## Intended Uses

HealthSynth is suitable for:

- Learning commercial analytics
- Data engineering practice
- BI and dashboard development
- SQL and DuckDB experimentation
- AI/LLM prototyping
- Data science workflows
- Demo environments
- Training and workshops

---

## Author

Virendra Pratap Singh
(https://www.linkedin.com/in/virendra-pratap-singh-iitg/)
NVA Dataworks

---

## License

MIT License