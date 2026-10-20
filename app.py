"""AI adoption vs productivity in Europe - Streamlit data narrative.

Every number on screen is read from data/processed/ (built by scripts/build_data.py).
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data" / "processed"
LAST_REFRESH = "19 October 2026"  # date the source samples were pulled from Eurostat
SOURCE_UPDATED = {"AI use (isoc_eb_ai)": "15 June 2026",
                  "Labour productivity (nama_10_lp_ulc)": "16 October 2026"}

# Okabe-Ito-style categorical order, validated for colour-vision deficiency.
# Fixed order: colour follows the country, never its rank.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
EU_GREY = "#52514e"
CONTEXT_GREY = "#b9b8b2"
MAX_COUNTRIES = 4

st.set_page_config(page_title="AI adoption vs productivity", layout="wide")


@st.cache_data
def load():
    ai = pd.read_csv(DATA / "ai_adoption.csv")
    pr = pd.read_csv(DATA / "productivity.csv")
    comp = pd.read_csv(DATA / "country_comparison.csv")
    return ai, pr, comp


ai, pr, comp = load()
SIZE_ORDER = ["GE10", "10-49", "50-249", "GE250"]
SIZE_LABEL = dict(ai[["size_emp", "firm_size"]].drop_duplicates().values)


def base_layout(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10),
                      plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(size=13), legend=dict(orientation="h", y=-0.2))
    fig.update_xaxes(showgrid=False, linecolor="#cccccc")
    fig.update_yaxes(gridcolor="#eeeeee", zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# Opening screen: the question, and something true about the whole dataset
# ---------------------------------------------------------------------------
st.title("Did the European countries whose firms adopted AI fastest see faster productivity growth?")

eu = ai[(ai.geo == "EU27_2020") & (ai.size_emp == "GE10")].set_index("year")["ai_adoption_pct"]
eu_p = pr[pr.geo == "EU27_2020"].set_index("year")["productivity_index_2020"]
g10 = comp[comp.size_emp == "GE10"]
r_raw = g10.ai_change_pp.corr(g10.prod_growth_2021_25_pct_pa)
r_trend = g10.ai_change_pp.corr(g10.prod_accel_pp)

c1, c2, c3 = st.columns(3)
c1.metric("EU-27 firms using AI, 2025", f"{eu[2025]:.2f}%",
          f"{eu[2025] - eu[2021]:+.1f} pp since 2021")
c2.metric("EU-27 labour productivity per hour, 2025", f"{eu_p[2025]:.1f}",
          f"{(eu_p[2025] / eu_p[2021] - 1) * 100:+.1f}% since 2021")
c3.metric("Countries compared", f"{len(g10)}")
c3.caption("26 EU members (Croatia lacks productivity data) + Norway, Serbia, Montenegro")
st.caption("AI use: % of enterprises with 10+ employees using at least one AI technology "
           "(Eurostat survey; no survey in 2022). Productivity: real output per hour worked, "
           "index 2020 = 100. All figures are for 2021-2025 unless stated.")

st.subheader("Answer")
st.markdown(
    f"**No, not yet.** Between 2021 and 2025 the share of EU firms using AI rose "
    f"{eu[2021]:.2f}% → {eu[2025]:.2f}%, but EU productivity per hour rose only "
    f"{(eu_p[2025] / eu_p[2021] - 1) * 100:.1f}% in total. Across {len(g10)} countries, "
    f"faster AI adoption went with *slower* productivity growth (correlation r = {r_raw:.2f}). "
    f"That negative link mostly disappears (r = {r_trend:.2f}) once each country is compared "
    f"with its own 2015-2019 trend: several fast adopters (Belgium, the Netherlands, Sweden) were already "
    f"slow-growing richer economies, while the fastest productivity growth came from catching-up economies "
    f"(Poland, Romania, Serbia) where AI use stayed low."
)

# ---------------------------------------------------------------------------
# Controls (one row)
# ---------------------------------------------------------------------------
st.divider()
countries = sorted(comp.country.unique())
f1, f2, f3 = st.columns([2, 1, 1])
picked = f1.multiselect(f"Highlight up to {MAX_COUNTRIES} countries", countries,
                        default=["Denmark", "Poland", "Germany", "Romania"],
                        max_selections=MAX_COUNTRIES)
size = f2.selectbox("Firm size", SIZE_ORDER, format_func=lambda s: SIZE_LABEL[s])
eu_only = f3.toggle("EU-27 members only", value=False)

colour = {c: SERIES[i] for i, c in enumerate(picked)}  # colour follows selection slot


# ---------------------------------------------------------------------------
# Chart 1 & 2: change over time
# ---------------------------------------------------------------------------
st.subheader("1 · AI use climbed fast; productivity barely moved")
if not picked:
    st.info("No countries selected. Pick at least one country above to compare it with the EU-27.")
else:
    left, right = st.columns(2)

    def line_chart(df, value, ytitle, fmt):
        fig = go.Figure()
        series = [("EU-27", EU_GREY)] + [(c, colour[c]) for c in picked]
        ends = []
        for name, col in series:
            d = df[df.country == name].sort_values("year")
            if d.empty:
                continue
            fig.add_trace(go.Scatter(x=d.year, y=d[value], name=name, mode="lines+markers",
                                     line=dict(color=col, width=2, dash="dot" if name == "EU-27" else "solid"),
                                     marker=dict(size=8)))
            last = d.iloc[-1]
            ends.append([last[value], last.year, f"{name} {last[value]:{fmt}}"])
        # nudge end labels apart so none overlap (min gap = 6% of the y-range)
        shown = df[df.country.isin([n for n, _ in series])][value]
        gap = (shown.max() - shown.min()) * 0.06 if len(shown) else 1
        ends.sort()
        prev = None
        for y, x, text in ends:
            ylab = y if prev is None else max(y, prev + gap)
            prev = ylab
            fig.add_annotation(x=x, y=ylab, text=text, xanchor="left", xshift=8,
                               showarrow=False, font=dict(size=12))
        years = sorted(df.year.unique())
        fig.update_xaxes(title="Year", tickvals=years, range=[years[0] - 0.3, years[-1] + 1.8])
        fig.update_yaxes(title=ytitle)
        return base_layout(fig)

    with left:
        d = ai[ai.size_emp == size]
        st.caption(f"**AI use**, % of firms using any AI technology, {SIZE_LABEL[size]}, 2021-2025 (no survey in 2022)")
        fig = line_chart(d, "ai_adoption_pct", "Firms using AI (%)", ".1f")
        st.plotly_chart(fig, use_container_width=True)
        if d[d.country.isin(picked)].empty:
            st.info("No AI data for the selected countries at this firm size.")
    with right:
        st.caption("**Labour productivity**, real output per hour worked, index 2020 = 100, 2015-2025")
        fig = line_chart(pr, "productivity_index_2020", "Index (2020 = 100)", ".1f")
        fig.add_vrect(x0=2020.5, x1=2025.5, fillcolor="#f2f2f0", line_width=0, layer="below")
        fig.add_annotation(x=2023, y=1, yref="paper", text="AI survey period", showarrow=False,
                           font=dict(size=11, color="#52514e"))
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Chart 3: ranking
# ---------------------------------------------------------------------------
st.subheader("2 · Who adopted most by 2025")
rank = comp[comp.size_emp == size]
if eu_only:
    rank = rank[rank.is_eu27]
if rank.empty:
    st.info("No countries match these filters. Try another firm size or switch off 'EU-27 members only'.")
else:
    rank = rank.sort_values("ai_2025_pct")
    cols = [colour.get(c, CONTEXT_GREY) for c in rank.country]
    fig = go.Figure(go.Bar(x=rank.ai_2025_pct, y=rank.country, orientation="h", marker_color=cols,
                           text=[f"{v:.1f}%" for v in rank.ai_2025_pct], textposition="outside",
                           textfont=dict(size=12)))
    fig.update_xaxes(title=f"Firms using AI in 2025 (%), {SIZE_LABEL[size]}",
                     range=[0, rank.ai_2025_pct.max() * 1.15])
    fig.update_yaxes(title=None)
    st.caption(f"**AI use in 2025 by country**, % of firms, {SIZE_LABEL[size]}, ranked. "
               f"Highlighted countries in colour.")
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode="show", bargap=0.25)
    st.plotly_chart(base_layout(fig, height=max(380, 24 * len(rank))), use_container_width=True)

# ---------------------------------------------------------------------------
# Chart 4: correlation (with baseline toggle)
# ---------------------------------------------------------------------------
st.subheader("3 · Did faster adopters get faster productivity growth?")
baseline = st.radio("Compare productivity growth…",
                    ["as it was (2021-2025, % per year)",
                     "against each country's own 2015-2019 trend (pp per year)"],
                    horizontal=True)
ycol = "prod_growth_2021_25_pct_pa" if baseline.startswith("as") else "prod_accel_pp"
ytitle = ("Productivity growth 2021-2025 (% per year)" if ycol.startswith("prod_growth")
          else "Growth 2021-25 minus growth 2015-19 (pp per year)")
sc = comp[comp.size_emp == size]
if eu_only:
    sc = sc[sc.is_eu27]
if len(sc) < 3:
    st.info("Too few countries match these filters to compare. Switch off 'EU-27 members only' or pick another firm size.")
else:
    r = sc.ai_change_pp.corr(sc[ycol])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sc.ai_change_pp, y=sc[ycol], mode="markers+text",
                             text=sc.geo, textposition="top center", textfont=dict(size=12),
                             marker=dict(size=10, color=[colour.get(c, CONTEXT_GREY) for c in sc.country],
                                         line=dict(color="white", width=2)),
                             hovertext=sc.country, showlegend=False))
    fig.add_hline(y=0, line_color="#999999", line_width=1)
    fig.update_xaxes(title=f"Change in firms using AI, 2021-2025 (percentage points), {SIZE_LABEL[size]}")
    pad = (sc[ycol].max() - sc[ycol].min()) * 0.12
    fig.update_yaxes(title=ytitle, range=[sc[ycol].min() - pad, sc[ycol].max() + pad])
    st.caption(f"**AI adoption change vs productivity growth**, one dot per country "
               f"(Eurostat codes, e.g. PL = Poland), n = {len(sc)}, correlation r = {r:.2f}. "
               f"Dots above 0 grew productivity / beat their own trend.")
    st.plotly_chart(base_layout(fig, height=440), use_container_width=True)
    direction = "negative" if r < 0 else "positive"
    verdict = ("no clear link" if abs(r) < 0.2 else
               f"a weak {direction} link" if abs(r) < 0.4 else f"a moderate {direction} link")
    st.markdown(f"With these settings there is **{verdict}** (r = {r:.2f}, {len(sc)} countries).")

# ---------------------------------------------------------------------------
# Chart 5: magnitude by firm size
# ---------------------------------------------------------------------------
st.subheader("4 · Large firms lead, small firms lag")
s = ai[(ai.geo == "EU27_2020") & (ai.size_emp != "GE10") & (ai.year.isin([2021, 2025]))].copy()
s["year"] = s["year"].astype(str)
order = [SIZE_LABEL[k] for k in ["10-49", "50-249", "GE250"]]
fig = px.bar(s, x="firm_size", y="ai_adoption_pct", color="year", barmode="group",
             category_orders={"firm_size": order, "year": ["2021", "2025"]},
             color_discrete_map={"2021": "#9ec5f0", "2025": "#2a78d6"},
             text=s.ai_adoption_pct.map(lambda v: f"{v:.1f}%"))
fig.update_traces(textposition="outside", marker_line_color="white", marker_line_width=2)
fig.update_xaxes(title="Firm size (number of employees)")
fig.update_yaxes(title="EU-27 firms using AI (%)", range=[0, s.ai_adoption_pct.max() * 1.15])
fig.update_layout(legend_title_text="Year", uniformtext_minsize=12, uniformtext_mode="show")
st.caption("**AI use by firm size, EU-27, 2021 vs 2025**, % of firms in each size class.")
st.plotly_chart(base_layout(fig), use_container_width=True)

# ---------------------------------------------------------------------------
# Limits, sources, refresh
# ---------------------------------------------------------------------------
st.divider()
st.subheader("What this data cannot show")
st.markdown("""
- **Cause and effect.** Countries differ in income, industry mix and post-COVID recovery. A correlation across ~29 countries cannot say AI caused or blocked anything.
- **How intensively AI is used.** Eurostat counts a firm as an adopter if it uses *any one* AI technology. A firm trialling a chatbot counts the same as one rebuilding its operations.
- **Time lags.** Only four survey years (2021, 2023, 2024, 2025). Productivity gains from new technology often take years to show up.
- **Firm-level gains.** Productivity here is whole-economy. Gains inside adopting firms could be real but too small to move national totals.
- **Gaps.** No AI survey in 2022. Croatia, Albania, Bosnia and Herzegovina and Türkiye lack productivity data in this release. Some recent values are provisional (flag *p*) or have a break in series (flag *b*).
""")

st.subheader("Sources")
st.markdown(f"""
- Eurostat, *Artificial intelligence by size class of enterprise* (`isoc_eb_ai`), indicator E_AI_TANY, NACE C10-S951_X_K. Source last updated {SOURCE_UPDATED['AI use (isoc_eb_ai)']}. https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table
- Eurostat, *Labour productivity and unit labour costs* (`nama_10_lp_ulc`), RLPR_HW, index 2020 = 100. Source last updated {SOURCE_UPDATED['Labour productivity (nama_10_lp_ulc)']}. https://ec.europa.eu/eurostat/databrowser/view/nama_10_lp_ulc/default/table
- Licence: Eurostat data is reusable under CC BY 4.0.

**Last data refresh: {LAST_REFRESH}.**
""")

with st.expander("Show the data behind the charts"):
    st.dataframe(comp[comp.size_emp == size], use_container_width=True, hide_index=True)
