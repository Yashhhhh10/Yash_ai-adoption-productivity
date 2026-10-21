# Data dictionary

All data comes from Eurostat and is reusable under **CC BY 4.0** (Eurostat copyright notice: https://ec.europa.eu/eurostat/about-us/policies/copyright).

Folder layout:

```
data/
  raw/         source samples exactly as pulled from the Eurostat API (only fields we use)
  processed/   files the app reads, rebuilt by scripts/build_data.py
```

Regenerate everything from the source samples (no internet needed):

```
python scripts/build_data.py
```

Re-download the source samples from Eurostat (needs internet):

```
python scripts/fetch_raw.py
```

---

## Source 1 · `raw/eurostat_isoc_eb_ai.csv`

| Field | Value |
|---|---|
| Source | Eurostat, *Artificial intelligence by size class of enterprise* (dataset `isoc_eb_ai`) |
| URL | https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table |
| API query | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/isoc_eb_ai?format=JSON&lang=EN&indic_is=E_AI_TANY&unit=PC_ENT&nace_r2=C10-S951_X_K` |
| Licence | CC BY 4.0 |
| Pulled | 19 October 2026 (Eurostat dataset last updated 15 June 2026) |
| Filter applied when pulling | indicator E_AI_TANY (uses at least one AI technology); unit % of enterprises; all non-financial sectors (NACE C10-S951_X_K); size classes 10-49, 50-249, 250+, 10+ only |
| Rows | 551 |
| Primary key | `size_emp` + `geo` + `time` |
| Time coverage | 2021, 2023, 2024, 2025 (no survey in 2022) |
| Latest observation | 2025 |
| Check total | sum of `value` = 10,388.47 (matches the API response) |

| Column | Meaning | Unit |
|---|---|---|
| `size_emp` | Firm size class: `10-49`, `50-249`, `GE250` (250+), `GE10` (10+, all) | code |
| `geo` | Country or aggregate (Eurostat code, e.g. `DE`, `EU27_2020`, `EA`) | code |
| `time` | Survey year | year |
| `value` | Enterprises using at least one AI technology | % of enterprises |
| `flag` | Eurostat flag: `b` = break in series, blank = none | code |

## Source 2 · `raw/eurostat_nama_10_lp_ulc.csv`

| Field | Value |
|---|---|
| Source | Eurostat, *Labour productivity and unit labour costs* (dataset `nama_10_lp_ulc`) |
| URL | https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table |
| API query | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_lp_ulc?format=JSON&lang=EN&na_item=RLPR_HW&unit=I20&sinceTimePeriod=2015` |
| Licence | CC BY 4.0 |
| Pulled | 19 October 2026 (Eurostat dataset last updated 16 October 2026) |
| Filter applied when pulling | RLPR_HW (real labour productivity per hour worked); unit index 2020 = 100; years 2015 onward |
| Rows | 407 |
| Primary key | `geo` + `time` |
| Time coverage | 2015-2025 |
| Latest observation | 2025 |
| Check total | sum of `value` = 40,296.171 (matches the API response) |

| Column | Meaning | Unit |
|---|---|---|
| `geo` | Country or aggregate (Eurostat code) | code |
| `time` | Year | year |
| `value` | Real labour productivity per hour worked | index, 2020 = 100 |
| `flag` | `p` = provisional, `b` = break in series, blank = none | code |

---

## Processed 1 · `processed/ai_adoption.csv`

**Transform** (`build_data.py`, step 1): from source 1, drop euro-area aggregates (EA, EA19 and so on, which overlap with the EU-27 and with countries); add country names and readable firm-size labels; flag EU-27 member states; rename `time` → `year` and `value` → `ai_adoption_pct`.

Rows: 535 · Primary key: `geo` + `size_emp` + `year` · Coverage: 2021, 2023-2025, 34 geographies (33 countries + EU-27) · Latest: 2025

| Column | Meaning | Unit |
|---|---|---|
| `geo` | Eurostat country code (`EU27_2020` = EU-27 total) | code |
| `country` | Country name | text |
| `is_eu27` | EU-27 member state | true/false |
| `size_emp` | Size class code | code |
| `firm_size` | Readable size label | text |
| `year` | Survey year | year |
| `ai_adoption_pct` | Enterprises using at least one AI technology | % of enterprises |
| `flag` | Eurostat flag | code |

## Processed 2 · `processed/productivity.csv`

**Transform** (`build_data.py`, step 2): from source 2, drop euro-area aggregates; add country names and the EU-27 flag; rename `time` → `year` and `value` → `productivity_index_2020`.

Rows: 352 · Primary key: `geo` + `year` · Coverage: 2015-2025, 32 geographies (31 countries + EU-27) · Latest: 2025

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_eu27` | as above | |
| `year` | Year | year |
| `productivity_index_2020` | Real output per hour worked | index, 2020 = 100 |
| `flag` | Eurostat flag | code |

## Processed 3 · `processed/country_comparison.csv`

**Transform** (`build_data.py`, step 3): for each size class, join each country's AI adoption in 2021 and 2025 with its productivity growth. Keep only countries present in both sources with no missing values (drops Croatia, Albania, Bosnia and Herzegovina and Türkiye, which lack productivity data, and the EU-27 total). Values rounded to 3 decimals.

- `ai_change_pp` = `ai_2025_pct` − `ai_2021_pct`
- `prod_growth_2021_25_pct_pa` = ((index₂₀₂₅ / index₂₀₂₁)^(1/4) − 1) × 100
- `prod_growth_2015_19_pct_pa` = ((index₂₀₁₉ / index₂₀₁₅)^(1/4) − 1) × 100 (pre-COVID baseline trend)
- `prod_accel_pp` = `prod_growth_2021_25_pct_pa` − `prod_growth_2015_19_pct_pa`

Rows: 114 (29 all firms, 28 small, 29 medium, 28 large) · Primary key: `geo` + `size_emp` · Coverage: adoption 2021→2025, productivity 2015→2025 · Latest: 2025

| Column | Meaning | Unit |
|---|---|---|
| `geo`, `country`, `is_eu27`, `size_emp` | as above | |
| `ai_2021_pct` | AI adoption in 2021 | % of enterprises |
| `ai_2025_pct` | AI adoption in 2025 | % of enterprises |
| `ai_change_pp` | Change in AI adoption, 2021-2025 | percentage points |
| `prod_growth_2021_25_pct_pa` | Average productivity growth, 2021-2025 | % per year |
| `prod_growth_2015_19_pct_pa` | Average productivity growth, 2015-2019 | % per year |
| `prod_accel_pp` | 2021-25 growth minus 2015-19 growth | percentage points per year |

Numbers computed in the app itself (not stored): correlation coefficient r (Pearson, `pandas.Series.corr`) between `ai_change_pp` and the chosen productivity column, for the filtered rows; EU-27 change since 2021 in the headline tiles.
