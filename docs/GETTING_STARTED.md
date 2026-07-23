# Getting Started with HealthSynth

Welcome!

HealthSynth is an open-source Python library for simulating pharmaceutical commercial markets and generating realistic, internally consistent datasets for learning analytics, data engineering, dashboarding, and experimentation.

Whether you're a data engineer, data scientist, BI developer, student, or simply curious about pharmaceutical analytics, this guide will help you generate your first simulated market in just a few minutes.

No prior pharmaceutical knowledge is required.


## Why HealthSynth?

Learning pharmaceutical commercial analytics is surprisingly difficult.

Real-world datasets are confidential.
Public datasets are limited.
Generic synthetic data generators can create realistic-looking tables, but they don't capture how pharmaceutical markets behave.

HealthSynth approaches the problem differently.

Instead of generating tables independently, it simulates a commercial market.

Products compete for market share.
Promotional activity influences adoption.
Commercial events such as product launches, loss of exclusivity, competitor entry, and market access affect the market over time.

The generated datasets are the result of those interactions.

This makes HealthSynth particularly useful for learning customer analytics, SQL, dashboard development, forecasting, and commercial data engineering.


## What you'll build

In this guide we'll generate a simulated oncology market containing:

- healthcare professionals
- commercial products
- promotional activity
- market demand
- market share
- prescriptions

HealthSynth will generate a collection of related datasets that remain internally consistent across the entire simulation.


## What you'll learn

By the end of this guide you'll know how to:

- generate your first HealthSynth market
- understand the generated datasets
- explore the commercial scenarios in studio
- use the included notebooks
- begin building your own simulations

## Prerequisites

You'll need:

- Python 3.11 or later
- Git (recommended)
- Jupyter Notebook or VS Code (optional, for running notebooks)

HealthSynth currently runs on Windows, macOS, and Linux.


## Installation

Clone the repository:

```bash
git clone https://github.com/vpsn99/healthsynth.git

cd healthsynth
```

Create a virtual environment.

### Windows

```powershell
python -m venv .venv

.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Install HealthSynth in editable mode:

```bash
pip install -e .
```
Streamlit is installed as part of the development dependencies and powers HealthSynth Studio.

Verify the installation:

```bash
healthsynth --help
```

If the installation was successful, you should see the available HealthSynth commands.


## Your First Simulation

HealthSynth includes several ready-to-use market profiles.

Let's begin with a new product launch scenario.

Run:

```bash
healthsynth generate \
    --config configs/profiles/oncology_product_launch.yaml \
    --hcps 500 \
    --output-dir output/tutorial
```

HealthSynth will generate a complete simulated pharmaceutical market.

Typical output looks similar to:

```text
HealthSynth generation started

Generation complete

Created 500 HCP records
Created 3 product records
Created ...
Output written to:
output/tutorial
```

## Explore the Simulation in HealthSynth Studio

```bash
    streamlit run ui/app.py
```
HealthSynth Studio provides an interactive way to explore generated commercial markets.

Using Studio you can:

generate commercial scenarios
compare datasets
replay commercial events on an interactive timeline
view key metrics and charts
inspect generated HCP and product data
download the generated datasets

## Understanding the Output

Open the output directory.

You'll find a collection of CSV files describing different parts of the simulated market.

| File | Description |
|------|-------------|
| market.csv | Market definition |
| hcp_master.csv | Healthcare professionals |
| product.csv | Product portfolio |
| call_activity.csv | Promotional activity |
| promotion_effect.csv | Promotion impact over time |
| market_demand.csv | Monthly market demand |
| market_share.csv | Product market share |
| prescriptions.csv | Generated NRx/TRx data |
| validation_report.md | Dataset validation summary |
| healthsynth_manifest.json | Generation metadata including HealthSynth version, schema version and locality configuration |

These datasets are linked together.

For example:

- market demand influences prescriptions
- promotional activity influences adoption
- commercial events influence market share
- market share influences prescription allocation

This relationship between datasets is one of the key ideas behind HealthSynth.


## Running the Notebooks

HealthSynth includes a set of Jupyter notebooks that explain both the generated data and the commercial concepts behind each scenario.

Open Jupyter Notebook or VS Code and navigate to the `notebooks` directory.

We recommend completing the notebooks in order.

| Notebook | Topic |
|-----------|-------|
| 01 | Running HealthSynth |
| 02 | Market Profiles |
| 03 | Competitor Products |
| 04 | DuckDB Analytics |
| 05 | Market Share |
| 06 | Market Demand |
| 07 | New Product Launch |
| 08 | Loss of Exclusivity |
| 09 | Competitor Launch |
| 10 | Market Access |

Each notebook combines business concepts with practical analysis of the generated datasets.
The notebooks build on one another, beginning with generation and progressing through commercial analytics concepts such as market demand, product launches, market access, and loss of exclusivity.

## Exploring Other Scenarios

Once you're comfortable generating your first market, try some of the other built-in commercial scenarios.

### Product Launch

Simulates the gradual adoption of a newly launched pharmaceutical product.

### Loss of Exclusivity (LOE)

Models the decline in market share after patent expiry and generic competition.

### Competitor Launch

Introduces a new competitor into an existing market and redistributes market share.

### Market Access

Simulates reimbursement or formulary improvements that increase a product's commercial opportunity.

### Localized Market Profiles

HealthSynth supports locality-aware synthetic identities.

```yaml
locality:
  faker_locale: ja_JP
  country_code: JP
```
Changing locality affects generated names, addresses, administrative areas, postal codes and phone numbers while leaving the commercial simulation unchanged.


Each scenario is fully configurable using YAML profiles.


## Where to Go Next

Congratulations!

You've generated your first HealthSynth simulation.

From here you can:

- modify an existing market profile
- create your own commercial scenarios
- analyse the generated data using SQL or DuckDB
- build dashboards in Power BI or Tableau
- develop forecasting or machine learning models
- work through the included notebooks

To learn more about how HealthSynth works internally-
- Explore additional Studio scenarios.
- Work through the notebooks.
- Modify YAML profiles.
- Read the Architecture Guide.
- Create your own commercial scenarios.


## Need Help?

If you encounter any issues:

- Check that you're using Python 3.11 or later.
- Verify that your virtual environment is activated.
- Ensure you've installed HealthSynth using `pip install -e .`.
- Review the generated `validation_report.md` for warnings or configuration issues.

If you discover a bug or have an idea for a new feature, please open an issue on GitHub.

## Reproducibility

HealthSynth is deterministic.

Running the same profile with the same seed produces identical datasets.

That is one of HealthSynth's design principles and a major advantage for learning, testing and demonstrations. It deserves a mention in a getting started guide.

---

HealthSynth was created to make pharmaceutical commercial analytics easier to learn through realistic, scenario-driven simulations.

We hope it helps you explore new ideas, build better analytics projects, and deepen your understanding of how commercial healthcare markets behave.