# AI adoption vs productivity in Europe

An interactive data narrative built with Streamlit, using public Eurostat data.

## The question

**Did the European countries whose firms adopted AI fastest see faster labour productivity growth between 2021 and 2025?**

It is arguable because the same data supports two readings. Taken at face value, faster AI adoption went with *slower* productivity growth (r = −0.37 across 29 countries). Compared with each country's own 2015-2019 trend, the link almost disappears (r = −0.06). Someone could reasonably argue "AI is not paying off" or "it is too early to tell" from the same numbers.

## Persona

**Elena, economic policy adviser at a national ministry in an EU member state.**

- **Task:** brief the minister on a proposed grant scheme that would subsidise AI adoption in small and medium-sized firms.
- **Decision:** whether to recommend the scheme on the grounds that AI adoption raises national productivity, and if so, which firm sizes to target.
- **Constraint:** she has one page and five minutes with the minister, needs evidence any EU colleague can check (official statistics only), and cannot commission new research before the budget deadline.

## User stories

1. **As a** policy adviser, **I want to** compare my country's AI adoption and productivity with the EU-27 over time, **so that** I can see whether rising AI use at home has come with rising productivity.
   *In the app:* pick countries in "Highlight up to 4 countries" → section 1 shows both trends side by side; section 2 shows where the country ranks.

2. **As a** policy adviser, **I want to** test whether countries that adopted AI faster also grew productivity faster, with and without each country's earlier trend, **so that** I do not justify public spending on a misleading correlation.
   *In the app:* section 3 scatter, switching the "Compare productivity growth…" option between raw growth and growth against the 2015-2019 trend. The sentence below the chart states the correlation for the current settings.

3. **As a** policy adviser, **I want to** see how AI adoption differs between small, medium and large firms, **so that** I can decide whether a subsidy should target small firms.
   *In the app:* section 4 shows the size gap for the EU-27; the "Firm size" filter re-draws sections 1-3 for one size class.

## Answer (as stated in the app)

No, not yet. EU firms using AI rose from 7.65% to 19.95% (2021-2025, firms with 10+ employees), while EU productivity per hour rose 1.3% in total. Several fast adopters (Belgium, the Netherlands, Sweden) were richer economies already growing slowly; the fastest productivity growth came from catching-up economies such as Poland, Romania and Serbia, whose AI adoption stayed low.

## Run it

```bash
pip install -r requirements.txt
python scripts/build_data.py     # rebuild data/processed/ from data/raw/
streamlit run app.py
```

## Repository layout

```
app.py                     the Streamlit app
requirements.txt
scripts/build_data.py      raw → processed transforms (offline, deterministic)
scripts/fetch_raw.py       re-downloads the raw samples from the Eurostat API
data/raw/                  source samples
data/processed/            files the app reads
data/DATA_DICTIONARY.md    every dataset: source, URL, licence, columns, units, key, coverage, transform
```

## Data sources

- Eurostat `isoc_eb_ai`, Artificial intelligence by size class of enterprise. CC BY 4.0.
- Eurostat `nama_10_lp_ulc`, Labour productivity and unit labour costs. CC BY 4.0.

Last data refresh: 19 October 2026. Full details in [data/DATA_DICTIONARY.md](data/DATA_DICTIONARY.md).
