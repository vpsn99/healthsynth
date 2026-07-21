# HealthSynth Data Model

**HealthSynth Version:** 0.2.0

**Schema Version:** 2.0


HealthSynth generates a set of related datasets representing a simulated pharmaceutical commercial market.

The datasets are not produced independently.

They describe different stages of one connected commercial system:

```text
Market and Product Configuration
                ↓
Healthcare Provider Population
                ↓
Promotional Activity
                ↓
Promotion Effect
                ↓
Market Demand
                ↓
Market Share
                ↓
Prescription Allocation
```

The purpose of this document is to explain:

- what each dataset represents
- the grain of each dataset
- the most important columns
- how datasets relate to one another
- which analytical questions each dataset can support

The exact schema may evolve as HealthSynth adds new capabilities, but the relationships described here form the core commercial data model.

---

# Data Model at a Glance

A typical HealthSynth simulation produces the following datasets:

| Dataset | Purpose |
|---|---|
| `market` | Defines the simulated commercial market |
| `hcp_master` | Contains healthcare providers participating in the market |
| `product` | Defines the competing product portfolio |
| `call_activity` | Records promotional interactions with HCPs |
| `promotion_effect` | Summarises promotional influence by product and month |
| `market_demand` | Defines the total monthly prescription opportunity |
| `market_share` | Allocates monthly market opportunity across products |
| `prescriptions` | Allocates product prescriptions across HCPs |

The output directory may also contain:

- a DuckDB database
- a dataset manifest
- a validation report

Schema 2.0 introduces locality-aware synthetic identities and generalizes administrative geography to support multiple countries.

---

# Relationship Overview

```text
market
  │
  ├───────────────┐
  │               │
  ▼               ▼
product       hcp_master
  │               │
  └──────┬────────┘
         ▼
   call_activity
         │
         ▼
 promotion_effect
         │
         ├──────────────┐
         │              │
         ▼              ▼
   market_share    market_demand
         │              │
         └──────┬───────┘
                ▼
         prescriptions
```

The primary shared identifiers are:

- `market_id`
- `product_id`
- `hcp_id`
- monthly date fields

---
# Locality Model


```text
Simulation configuration

↓

Commercial assumptions

↓

Locality configuration

↓

Synthetic identities

↓

Generated datasets
```

| Property      | Meaning                                             |
| ------------- | --------------------------------------------------- |
| faker_locale  | Faker locale used for synthetic identity generation |
| country_code  | ISO-like country identifier                         |
| country_name  | Human-readable country name                         |
| currency_code | Currency metadata                                   |
| timezone      | Market timezone                                     |


Locality influences identity generation and metadata only. It does not automatically modify commercial assumptions such as demand, market share, promotion, seasonality, or competitive behaviour.

---
# Common Analytical Grains

HealthSynth uses several different dataset grains.

Understanding grain is essential before joining or aggregating data.

| Dataset | Grain |
|---|---|
| `market` | One row per market |
| `hcp_master` | One row per HCP |
| `product` | One row per product |
| `call_activity` | One row per promotional interaction |
| `promotion_effect` | One row per product and month |
| `market_demand` | One row per therapeutic area and month |
| `market_share` | One row per product, therapeutic area, and month |
| `prescriptions` | One row per HCP, product, and month |

A dataset should always be interpreted at its native grain before aggregation.

---

# 1. Market

## Purpose

The `market` dataset defines the commercial environment being simulated.

It provides the market identity shared by downstream datasets.

## Grain

One row per market.

## Typical Key

```text
market_id
```

## Important Columns

| Column | Meaning |
|---|---|
| `market_id` | Unique market identifier |
| `market_name` | Human-readable market name |
| `country` | Country represented by the simulation |
| `therapeutic_area` | Primary disease or commercial area, when present |

Additional fields may be included as the market model expands.

## Used By

The market identifier is referenced by:

- `product`
- `call_activity`
- `promotion_effect`
- `market_demand`
- `market_share`
- `prescriptions`

## Example Questions

- Which country does this simulation represent?
- Which therapeutic area is being modelled?
- How many markets exist in the generated output?

---

# 2. HCP Master

## Purpose

The `hcp_master` dataset contains the healthcare providers who participate in the simulated commercial market.

HCP attributes influence:

- promotional targeting
- call activity
- product affinity
- prescription allocation
- territory analysis

## Grain

One row per healthcare provider.

## Typical Key

```text
hcp_id
```

## Important Columns

| Column | Meaning |
|---|---|
| `hcp_id` | Unique HCP identifier |
| `specialty` | Healthcare provider specialty |
| `decile` | Relative prescribing-potential classification |
| `segment` | Commercial HCP segment |
| `territory_id` | Assigned commercial territory |
| `rep_id` | Assigned representative |
| `market_id` | Market to which the HCP belongs |

The exact attributes may vary by profile.

## Generated From

The HCP population is influenced by configuration such as:

- specialty distribution
- decile distribution
- segmentation assumptions
- territory count
- market size

## Referenced By

- `call_activity`
- `prescriptions`

## Example Questions

- How many HCPs exist in each specialty?
- What is the distribution of HCP deciles?
- Which territories contain the most high-potential HCPs?
- How many HCPs are assigned to each representative?
- Which HCP segments generate the most prescriptions?

---

# 3. Product

## Purpose

The `product` dataset defines the pharmaceutical products competing within the simulated market.

Products are commercial entities rather than simple lookup records.

Their attributes influence:

- product availability
- market share
- promotional activity
- launch adoption
- loss of exclusivity
- market access
- prescription allocation

## Grain

One row per product.

## Typical Key

```text
product_id
```

## Important Columns

| Column | Meaning |
|---|---|
| `product_id` | Unique product identifier |
| `product_name` | Human-readable brand name |
| `market_id` | Market in which the product competes |
| `therapeutic_area` | Product therapeutic area |
| `manufacturer` | Product manufacturer |
| `brand_type` | Commercial product classification |
| `launch_date` | Date from which the product becomes active |
| `baseline_market_share` | Configured competitive starting assumption |
| `status` | Product status |

Scenario-specific columns may include:

| Column | Meaning |
|---|---|
| `adoption_curve` | Shape of product adoption after launch |
| `adoption_months` | Time required to reach mature adoption |
| `launch_share_factor` | Initial launch adoption level |
| `promotion_adoption_weight` | Strength of promotion-driven acceleration |
| `share_source_weights` | Competitors from which launch share is sourced |
| `loe_date` | Loss-of-exclusivity date |
| `loe_erosion_months` | Duration of LOE erosion |
| `post_loe_share_factor` | Remaining competitive strength after LOE |
| `market_access_date` | Effective date of access change |
| `market_access_factor` | Commercial effect of access improvement or restriction |

## Referenced By

- `call_activity`
- `promotion_effect`
- `market_share`
- `prescriptions`

## Example Questions

- Which products compete in the market?
- Which company manufactures each product?
- Which products are mature versus recently launched?
- Which product has the highest baseline share?
- Which product is approaching loss of exclusivity?
- Which product receives improved market access?

---

# 4. Call Activity

## Purpose

The `call_activity` dataset records simulated promotional interactions between products and healthcare providers.

Despite the dataset name, activity may represent multiple channels, not only representative calls.

Examples include:

- representative calls
- email
- webinars
- conferences
- digital promotion

## Grain

One row per promotional interaction.

## Typical Key

```text
call_id
```

## Foreign Keys

```text
market_id
hcp_id
product_id
rep_id
```

## Important Columns

| Column | Meaning |
|---|---|
| `call_id` | Unique interaction identifier |
| `call_date` | Date of promotional activity |
| `hcp_id` | HCP receiving the interaction |
| `rep_id` | Representative associated with the interaction |
| `product_id` | Product being promoted |
| `channel` | Promotional channel |
| `sample_dropped` | Whether a sample was provided |
| `market_id` | Associated market |

## Generated From

Call activity is influenced by:

- HCP decile
- HCP segment
- product availability
- channel distribution
- simulation timeline
- random seed

Products do not receive call activity before their launch date.

## Used By

Call activity contributes to:

- `promotion_effect`
- HCP engagement analysis
- channel-mix analysis
- call-frequency analysis

## Example Questions

- Which products received the most promotional activity?
- Which HCP specialties were called most often?
- Which channels were used most frequently?
- How did call volume change over time?
- Which representatives generated the most activity?
- Did a launch product receive calls only after launch?

---

# 5. Promotion Effect

## Purpose

The `promotion_effect` dataset summarises the monthly influence of promotional activity on each product.

It converts raw promotional interactions into a product-level commercial signal that can influence market-share behaviour.

## Grain

One row per product and month.

Depending on the implementation, market or therapeutic-area fields may also be present.

## Typical Composite Key

```text
month
product_id
```

## Important Columns

Typical columns may include:

| Column | Meaning |
|---|---|
| `month` | Monthly simulation period |
| `product_id` | Product receiving the promotional effect |
| `promotion_index` | Normalised measure of promotional influence |
| `market_id` | Associated market |

The exact promotion metrics may evolve as additional channels and response models are added.

## Generated From

- `call_activity`
- channel-response assumptions
- product-level engagement
- monthly aggregation

## Used By

- market-share calculation
- launch adoption acceleration
- promotion analytics

## Example Questions

- Which product received the strongest promotional support?
- How did promotional influence change over time?
- Did promotion accelerate adoption after launch?
- Which months had unusually high promotional intensity?

---

# 6. Market Demand

## Purpose

The `market_demand` dataset defines the total prescription opportunity available in each month.

It describes the size of the market before that opportunity is divided across products.

## Grain

One row per:

```text
market
therapeutic area
month
```

## Typical Composite Key

```text
market_id
therapeutic_area
month
```

## Important Columns

| Column | Meaning |
|---|---|
| `market_id` | Associated market |
| `month` | Monthly simulation period |
| `therapeutic_area` | Therapeutic market |
| `base_market_nrx` | Starting monthly prescription opportunity |
| `growth_factor` | Cumulative market-growth factor |
| `seasonality_factor` | Seasonal monthly adjustment |
| `market_nrx` | Final simulated market demand |

## Conceptual Calculation

```text
Base Market NRx
        ×
Growth Factor
        ×
Seasonality Factor
        =
Monthly Market NRx
```

The final value is represented as a whole number.

## Used By

- `prescriptions`
- product-level demand allocation
- market-growth analysis
- seasonality analysis

## Example Questions

- Is the market growing or shrinking?
- Which months have the strongest seasonal demand?
- How large is the total prescribing opportunity?
- Can a product lose share while still gaining prescriptions?
- How does market growth affect total NRx?

---

# 7. Market Share

## Purpose

The `market_share` dataset describes how monthly market demand is divided among competing products.

It is both:

- an analytical output
- an upstream input into prescription allocation

## Grain

One row per:

```text
market
therapeutic area
product
month
```

## Typical Composite Key

```text
market_id
therapeutic_area
product_id
month
```

## Important Columns

| Column | Meaning |
|---|---|
| `market_id` | Associated market |
| `month` | Monthly simulation period |
| `therapeutic_area` | Therapeutic market |
| `product_id` | Product identifier |
| `baseline_market_share` | Configured competitive assumption |
| `base_adoption_factor` | Natural post-launch adoption level |
| `promotion_acceleration` | Additional adoption from promotion |
| `effective_adoption_factor` | Final adoption level after acceleration |
| `loe_factor` | Remaining competitive strength after LOE |
| `market_access_factor` | Commercial effect of market access |
| `adjusted_market_share` | Final monthly product market share |

Some fields may remain neutral when a scenario is not configured.

Examples:

```text
loe_factor = 1.0
market_access_factor = 1.0
```

## Business Rule

Within each therapeutic area and month:

```text
Sum of adjusted_market_share = 1.0
```

## Generated From

- product baseline share
- product availability
- promotion effect
- adoption logic
- commercial events
- controlled variation
- competitive normalization

## Used By

- `prescriptions`
- competitive performance analysis
- launch analysis
- LOE analysis
- market-access analysis

## Example Questions

- Which product is gaining share?
- How did share change after a launch?
- Which incumbent lost the most share?
- What happened after loss of exclusivity?
- Did improved market access result in a sustained share gain?
- Does monthly share always sum to 100%?

---

# 8. Prescriptions

## Purpose

The `prescriptions` dataset contains generated product-level prescription volume allocated across healthcare providers.

Prescription records are the downstream result of:

- market demand
- adjusted market share
- HCP attributes
- product affinity
- promotional engagement

They are not generated independently.

## Grain

One row per:

```text
market
month
HCP
product
```

## Typical Key

```text
rx_id
```

## Foreign Keys

```text
market_id
hcp_id
product_id
```

## Important Columns

| Column | Meaning |
|---|---|
| `rx_id` | Unique prescription-row identifier |
| `rx_date` | Monthly prescription date |
| `hcp_id` | HCP receiving the prescription allocation |
| `product_id` | Product prescribed |
| `nrx` | New prescriptions |
| `trx` | Total prescriptions |
| `market_id` | Associated market |

## Conceptual Allocation

```text
Monthly Market Demand
        ×
Adjusted Market Share
        =
Product NRx
        ↓
Allocated Across HCPs
```

The HCP allocation may be influenced by:

- specialty affinity
- HCP decile
- promotional engagement
- product configuration

## Business Rule

For each month:

```text
Sum of generated NRx
        =
Simulated market NRx
```

Small product-level rounding differences may occur because prescriptions are represented as integers, but the monthly market total is preserved.

## Example Questions

- Which products generated the highest NRx?
- Which HCP specialties generated the most prescriptions?
- Which HCPs have the highest product volume?
- How did prescriptions change after a launch?
- Did a product gain NRx despite losing market share?
- Which territories generated the highest prescribing volume?

---

# Common Join Paths

## Products and Prescriptions

```sql
SELECT
    rx.rx_date,
    p.product_name,
    SUM(rx.nrx) AS total_nrx
FROM prescriptions AS rx
JOIN product AS p
    ON rx.product_id = p.product_id
GROUP BY
    rx.rx_date,
    p.product_name;
```

Use this join to analyse product prescription performance.

---

## HCPs and Prescriptions

```sql
SELECT
    h.specialty,
    SUM(rx.nrx) AS total_nrx
FROM prescriptions AS rx
JOIN hcp_master AS h
    ON rx.hcp_id = h.hcp_id
GROUP BY
    h.specialty;
```

Use this join for specialty, segment, decile, or territory analysis.

---

## HCPs and Call Activity

```sql
SELECT
    h.specialty,
    c.channel,
    COUNT(*) AS interactions
FROM call_activity AS c
JOIN hcp_master AS h
    ON c.hcp_id = h.hcp_id
GROUP BY
    h.specialty,
    c.channel;
```

Use this join to examine promotional targeting.

---

## Market Share and Products

```sql
SELECT
    ms.month,
    p.product_name,
    ms.adjusted_market_share
FROM market_share AS ms
JOIN product AS p
    ON ms.product_id = p.product_id
ORDER BY
    ms.month,
    p.product_name;
```

Use this join to analyse competitive movement.

---

## Market Demand and Market Share

```sql
SELECT
    ms.month,
    ms.product_id,
    md.market_nrx,
    ms.adjusted_market_share,
    md.market_nrx * ms.adjusted_market_share
        AS expected_product_nrx
FROM market_share AS ms
JOIN market_demand AS md
    ON ms.market_id = md.market_id
    AND ms.therapeutic_area = md.therapeutic_area
    AND ms.month = md.month;
```

Use this relationship to understand product demand allocation.

---

# Date Fields

Several datasets use monthly dates:

| Dataset | Date Column |
|---|---|
| `call_activity` | `call_date` |
| `promotion_effect` | `month` |
| `market_demand` | `month` |
| `market_share` | `month` |
| `prescriptions` | `rx_date` |

`market_demand`, `market_share`, and `prescriptions` generally represent monthly simulation periods.

`call_activity` may contain individual dates within a month.

When joining monthly datasets, convert dates to a consistent month-level representation.

Example in pandas:

```python
market_share["month"] = pd.to_datetime(
    market_share["month"]
)

prescriptions["rx_date"] = pd.to_datetime(
    prescriptions["rx_date"]
)
```

---

# Configuration Model

```text
market
    ↓
market.csv

products
    ↓
product.csv

locality
    ↓
hcp_master.csv

events
    ↓
market_share.csv

promotion
    ↓
promotion_effect.csv
```


---
# Core Business Rules

HealthSynth maintains several important consistency rules.

## Product References Must Be Valid

Every `product_id` appearing in transactional or analytical datasets must exist in the product master.

## HCP References Must Be Valid

Every `hcp_id` in calls or prescriptions must exist in the HCP master.

## Product Availability Is Time-Aware

A product should not receive:

- market share
- promotional activity
- prescriptions

before its configured launch date.

## Market Share Must Reconcile

For each month and therapeutic area:

```text
Total adjusted market share = 100%
```

## Prescriptions Must Reconcile

For each month:

```text
Total generated NRx = market NRx
```

## Simulations Are Reproducible

The same:

- configuration
- generation parameters
- random seed

should produce the same output.

---

# Typical Analytical Questions

The generated data model can support questions such as:

## Customer Analytics

- Which HCP segments generate the most NRx?
- Which specialties receive the most promotional activity?
- Which HCPs are highly engaged but under-prescribing?
- How does prescription volume vary by territory?

## Product Analytics

- Which products are gaining market share?
- How does promotion relate to product adoption?
- Which product gained the most NRx?
- How does baseline share compare with adjusted share?

## Market Analytics

- Is the market growing?
- Which months have the strongest seasonal demand?
- Can products gain volume while losing share?
- How does total demand reconcile with prescriptions?

## Scenario Analytics

- What happens after a new product launch?
- Which incumbent loses the most share?
- How quickly does a product erode after LOE?
- What is the impact of improved market access?
- How does competitor entry change prescription allocation?

---

# Example Analytical Flow

A common HealthSynth analysis may follow this sequence:

```text
1. Inspect market and product definitions

2. Understand the HCP population

3. Analyse promotional activity

4. Review market demand

5. Compare adjusted market share

6. Aggregate prescriptions

7. Reconcile outputs

8. Interpret the commercial story
```

This mirrors the underlying simulation pipeline.

---

# Data Model Summary

HealthSynth's data model is built around connected commercial relationships.

```text
HCPs and Products
        ↓
Promotional Activity
        ↓
Commercial Effects
        ↓
Market Demand and Share
        ↓
Prescription Allocation
```

The model is intended to help users understand not only the generated values, but also the business processes that produced them.

For implementation details, see:

```text
docs/ARCHITECTURE.md
```

For the first hands-on simulation, see:

```text
docs/GETTING_STARTED.md
```

---

# Schema Evolution


| Schema | Changes                                                             |
| ------ | ------------------------------------------------------------------- |
| 1.0    | Initial commercial analytics model                                  |
| 2.0    | Locality-aware identities, administrative_area, expanded HCP schema |

---

# Data Generation Pipeline

```text
Configuration

↓

Market

↓

HCPs

↓

Products

↓

Commercial Events

↓

Promotion

↓

Market Demand

↓

Market Share

↓

Prescriptions
```