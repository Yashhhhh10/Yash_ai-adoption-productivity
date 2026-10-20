# AI use notes, for your provenance matrix row(s)

The brief needs one row per substantive AI use, with columns: artefact, who, tool, what was asked, what came back, how it was verified (naming a check that could have failed), outcome. Here are draft rows covering what Claude did for you. **Run the checks yourself before submitting** so the verification column is true.

| Artefact | Who | Tool | What was asked | What came back | How it was verified (a check that could have failed) | Outcome |
|---|---|---|---|---|---|---|
| `data/raw/*.csv` | [your name] | Claude (Anthropic) | Find public data on AI adoption and productivity, and pull it from Eurostat | Two Eurostat API extracts (`isoc_eb_ai`, `nama_10_lp_ulc`) | Row count and sum of `value` compared with the Eurostat API response (551 rows / 10,388.47 and 407 rows / 40,296.171). Spot-check: EU-27 2025 AI adoption = 19.95% matches the Eurostat data browser. Either could have mismatched. | Kept |
| `scripts/build_data.py`, `data/processed/` | [your name] | Claude | Write a reproducible transform from raw to processed | Python script producing 3 processed files | Deleted `data/processed/`, re-ran the script, and the output was byte-identical. Hand-checked Poland's productivity growth: (117.0 / 101.159)^(1/4) − 1 = 3.70% per year, matching the file. | Kept |
| `app.py` | [your name] | Claude | Build a Streamlit app with 4+ charts, 2+ interactions and an empty-filter state | Streamlit app with 5 charts and 4 controls | Loaded at 1366×768 with no horizontal scroll; cleared all countries and the empty-state message appeared; each control re-rendered in under 0.5 s. Colours passed a colour-vision-deficiency validator. | Kept, with label fixes |
| `VIDEO_SCRIPT.md` | [your name] | Claude | Draft a video script and talking points | Script with a source table for every number | Each spoken number traced to a row in the processed files (table at the end of the script). One claim, that Finland was slow-growing before 2020, failed the check (its 2015-19 growth was 1.09% a year, above the EU's 0.93%) and was removed. | Edited |

## Data and AI disclosure statement (draft sentence you can adapt)

> I used Claude (Anthropic) to locate Eurostat datasets, write the data-processing script and Streamlit app, and draft my video script. I checked every number shown in the app and said in the video against the processed data files, and re-ran the processing script to confirm the outputs regenerate exactly. The interpretation and recorded presentation are my own.
