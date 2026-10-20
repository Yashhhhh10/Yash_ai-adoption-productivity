"""Rebuild every processed file in data/processed/ from the source samples in data/raw/.

Run from the repo root:  python scripts/build_data.py
No network access needed. Same inputs always give the same outputs.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Country names (Eurostat geo codes). Aggregates are kept separately.
NAMES = {
    "BE": "Belgium", "BG": "Bulgaria", "CZ": "Czechia", "DK": "Denmark", "DE": "Germany",
    "EE": "Estonia", "IE": "Ireland", "EL": "Greece", "ES": "Spain", "FR": "France",
    "HR": "Croatia", "IT": "Italy", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania",
    "LU": "Luxembourg", "HU": "Hungary", "MT": "Malta", "NL": "Netherlands", "AT": "Austria",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SI": "Slovenia", "SK": "Slovakia",
    "FI": "Finland", "SE": "Sweden", "NO": "Norway", "IS": "Iceland", "CH": "Switzerland",
    "ME": "Montenegro", "RS": "Serbia", "AL": "Albania", "BA": "Bosnia and Herzegovina",
    "TR": "Türkiye", "EU27_2020": "EU-27",
}
SIZE_LABELS = {"10-49": "small firms (10-49)", "50-249": "medium firms (50-249)",
               "GE250": "large firms (250+)", "GE10": "all firms (10+ employees)"}
EU27 = ["BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV",
        "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"]


def keep(df):
    """Drop euro-area aggregates (EA, EA19...) - they overlap with EU-27 and countries."""
    return df[df["geo"].isin(NAMES)].copy()


# 1. AI adoption, long format ---------------------------------------------------
ai = keep(pd.read_csv(RAW / "eurostat_isoc_eb_ai.csv"))
ai["country"] = ai["geo"].map(NAMES)
ai["firm_size"] = ai["size_emp"].map(SIZE_LABELS)
ai["is_eu27"] = ai["geo"].isin(EU27)
ai = ai.rename(columns={"time": "year", "value": "ai_adoption_pct"})
ai["flag"] = ai["flag"].fillna("")
ai = ai[["geo", "country", "is_eu27", "size_emp", "firm_size", "year", "ai_adoption_pct", "flag"]]
ai.sort_values(["size_emp", "geo", "year"]).to_csv(OUT / "ai_adoption.csv", index=False)

# 2. Labour productivity, long format -------------------------------------------
pr = keep(pd.read_csv(RAW / "eurostat_nama_10_lp_ulc.csv"))
pr["country"] = pr["geo"].map(NAMES)
pr["is_eu27"] = pr["geo"].isin(EU27)
pr = pr.rename(columns={"time": "year", "value": "productivity_index_2020"})
pr["flag"] = pr["flag"].fillna("")
pr = pr[["geo", "country", "is_eu27", "year", "productivity_index_2020", "flag"]]
pr.sort_values(["geo", "year"]).to_csv(OUT / "productivity.csv", index=False)

# 3. Country comparison table (one row per country x firm size) ------------------
#    Adoption change 2021->2025 and productivity growth over the same window,
#    plus each country's own pre-AI-survey trend (2015->2019) as a baseline.
p = pr.pivot(index="geo", columns="year", values="productivity_index_2020")
growth = pd.DataFrame({
    "prod_growth_2021_25_pct_pa": ((p[2025] / p[2021]) ** (1 / 4) - 1) * 100,
    "prod_growth_2015_19_pct_pa": ((p[2019] / p[2015]) ** (1 / 4) - 1) * 100,
})
growth["prod_accel_pp"] = growth["prod_growth_2021_25_pct_pa"] - growth["prod_growth_2015_19_pct_pa"]

rows = []
for size, g in ai.groupby("size_emp"):
    a = g.pivot(index="geo", columns="year", values="ai_adoption_pct")
    t = pd.DataFrame({
        "size_emp": size,
        "ai_2021_pct": a.get(2021),
        "ai_2025_pct": a.get(2025),
    })
    t["ai_change_pp"] = t["ai_2025_pct"] - t["ai_2021_pct"]
    rows.append(t.join(growth, how="inner"))
comp = pd.concat(rows).reset_index().rename(columns={"index": "geo"})
comp = comp[comp["geo"] != "EU27_2020"].dropna()
comp.insert(1, "country", comp["geo"].map(NAMES))
comp.insert(2, "is_eu27", comp["geo"].isin(EU27))
comp = comp.round(3)
comp.sort_values(["size_emp", "geo"]).to_csv(OUT / "country_comparison.csv", index=False)

print("ai_adoption.csv       ", len(ai), "rows")
print("productivity.csv      ", len(pr), "rows")
print("country_comparison.csv", len(comp), "rows")
