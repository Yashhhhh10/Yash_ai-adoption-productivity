"""Re-download the two source samples in data/raw/ from the Eurostat API.

Run from the repo root (needs internet):  python scripts/fetch_raw.py
Then rebuild the processed files:         python scripts/build_data.py

Values may change slightly if Eurostat has revised its data since 19 October 2026.
"""
from pathlib import Path
import json
import urllib.request

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
SOURCES = {
    "eurostat_isoc_eb_ai.csv": (
        "isoc_eb_ai?format=JSON&lang=EN&indic_is=E_AI_TANY&unit=PC_ENT&nace_r2=C10-S951_X_K",
        ["size_emp", "geo", "time"],
        {"size_emp": {"10-49", "50-249", "GE250", "GE10"}},
    ),
    "eurostat_nama_10_lp_ulc.csv": (
        "nama_10_lp_ulc?format=JSON&lang=EN&na_item=RLPR_HW&unit=I20&sinceTimePeriod=2015",
        ["geo", "time"],
        {},
    ),
}


def jsonstat_rows(j, keep_dims, filters):
    """Flatten a Eurostat JSON-stat response into (dims..., value, flag) rows."""
    ids, sizes = j["id"], j["size"]
    codes = []
    for d in ids:
        idx = j["dimension"][d]["category"]["index"]
        arr = [None] * len(idx)
        for k, v in idx.items():
            arr[v] = k
        codes.append(arr)
    status = j.get("status", {})
    for key, value in sorted(j["value"].items(), key=lambda kv: int(kv[0])):
        i, rem, c = int(key), int(key), {}
        for pos in range(len(ids) - 1, -1, -1):
            c[ids[pos]] = codes[pos][rem % sizes[pos]]
            rem //= sizes[pos]
        if any(c[d] not in allowed for d, allowed in filters.items()):
            continue
        yield [c[d] for d in keep_dims] + [value, status.get(str(i), "")], c


for fname, (query, dims, filters) in SOURCES.items():
    with urllib.request.urlopen(BASE + query, timeout=60) as r:
        j = json.load(r)
    rows = [r for r, _ in jsonstat_rows(j, dims, filters)]
    with open(RAW / fname, "w") as f:
        f.write(",".join(dims + ["value", "flag"]) + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print(f"{fname}: {len(rows)} rows (source updated {j.get('updated')})")
