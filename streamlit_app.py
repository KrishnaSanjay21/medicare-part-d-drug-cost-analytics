from __future__ import annotations

import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import executive_metrics, quality_results, state_summary, top_drugs
from src.bootstrap import ensure_database_ready
from src.config import DATABASE, DATASET_PAGE, DATA_YEAR

st.set_page_config(page_title="Part D Atlas", page_icon="Rx", layout="wide")

NAVY = "#123047"
BLUE = "#2374AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
RED = "#D95D5D"
LIGHT = "#F3F7FA"

st.markdown(
    f"""
    <style>
      .stApp {{ background: {LIGHT}; color: {NAVY}; }}
      [data-testid="stAppViewContainer"],
      [data-testid="stAppViewContainer"] p,
      [data-testid="stAppViewContainer"] label,
      [data-testid="stAppViewContainer"] h1,
      [data-testid="stAppViewContainer"] h2,
      [data-testid="stAppViewContainer"] h3 {{ color: {NAVY} !important; }}
      [data-testid="stMetric"] {{
        background: white;
        border: 1px solid #D9E3EA;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(18, 48, 71, 0.05);
      }}
      [data-testid="stMetricLabel"],
      [data-testid="stMetricLabel"] p {{ color: #4B6475 !important; }}
      [data-testid="stMetricValue"],
      [data-testid="stMetricValue"] div {{ color: {NAVY} !important; }}
      [data-testid="stCaptionContainer"],
      [data-testid="stCaptionContainer"] p {{ color: #566B79 !important; }}
      .scope-note {{
        background: white;
        color: #334E60 !important;
        border-left: 4px solid {BLUE};
        padding: 12px 16px;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(18, 48, 71, 0.04);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


def show_chart(fig: go.Figure) -> None:
    """Render charts with a stable light theme on local and hosted deployments."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(color=NAVY),
        title_font=dict(color=NAVY),
    )
    st.plotly_chart(fig, width="stretch", theme=None)


@st.cache_data(show_spinner=False)
def read_sql(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DATABASE) as connection:
        return pd.read_sql_query(sql, connection)


@st.cache_resource(show_spinner=False)
def bootstrap_database():
    return ensure_database_ready()


def money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.1f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    return f"${value:,.0f}"


def count(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:,.1f}M"
    return f"{value:,.0f}"


if not DATABASE.exists():
    st.title("Part D Atlas")
    st.info("First launch: downloading the published CMS file and building the analytical database.")
    try:
        with st.spinner("Preparing the 2024 CMS Medicare Part D data…"):
            bootstrap_database()
    except Exception as exc:
        st.error("The CMS dataset could not be prepared. Please reboot the Streamlit app and try again.")
        st.caption(f"{type(exc).__name__}: {exc}")
        st.stop()

page = st.sidebar.radio(
    "View",
    ["Executive Summary", "Drug Analysis", "State Comparison", "Data Quality & Methodology"],
)
st.sidebar.caption(f"CMS Medicare Part D public-use data, {DATA_YEAR}")

if page == "Executive Summary":
    st.title("Part D Atlas")
    st.caption("Medicare Part D drug cost and prescribing analytics")
    st.markdown(
        '<div class="scope-note">National totals use CMS national rows only. State rows are used only for state comparisons to prevent double-counting.</div>',
        unsafe_allow_html=True,
    )
    metrics = executive_metrics()
    cols = st.columns(5)
    cols[0].metric("Total claims", count(metrics.total_claims))
    cols[1].metric("Total drug cost", money(metrics.total_drug_cost))
    cols[2].metric("30-day fills", count(metrics.total_30day_fills))
    cols[3].metric("Cost per claim", money(metrics.cost_per_claim))
    cols[4].metric("Distinct drugs", f"{int(metrics.distinct_drugs):,}")

    left, right = st.columns([1.15, 1])
    top = top_drugs(12)
    with left:
        fig = px.bar(
            top.sort_values("tot_drug_cst"),
            x="tot_drug_cst",
            y="brnd_name",
            orientation="h",
            color_discrete_sequence=[BLUE],
            labels={"tot_drug_cst": "Total drug cost", "brnd_name": "Brand"},
            title="Highest-cost drugs",
        )
        fig.update_layout(height=500, margin=dict(l=10, r=15, t=55, b=10), xaxis_tickformat="$,.2s")
        show_chart(fig)
    with right:
        states = state_summary().head(12).sort_values("total_drug_cost")
        fig = px.bar(
            states,
            x="total_drug_cost",
            y="state_code",
            orientation="h",
            color_discrete_sequence=[TEAL],
            labels={"total_drug_cost": "Total drug cost", "state_code": "State"},
            title="States with the highest total drug cost",
        )
        fig.update_layout(height=500, margin=dict(l=10, r=15, t=55, b=10), xaxis_tickformat="$,.2s")
        show_chart(fig)

elif page == "Drug Analysis":
    st.title("Drug Analysis")
    top_n = st.slider("Number of drugs", min_value=10, max_value=50, value=20, step=5)
    drugs = top_drugs(top_n)
    left, right = st.columns([1.1, 1])
    with left:
        fig = px.bar(
            drugs.sort_values("tot_drug_cst"),
            x="tot_drug_cst",
            y="brnd_name",
            orientation="h",
            color="opioid_drug_flag",
            color_discrete_map={"Y": RED, "N": BLUE, "": "#8CA0AE"},
            title="Total drug cost by brand",
            labels={"tot_drug_cst": "Total drug cost", "brnd_name": "Brand", "opioid_drug_flag": "Opioid"},
        )
        fig.update_layout(height=max(500, top_n * 24), xaxis_tickformat="$,.2s")
        show_chart(fig)
    with right:
        scatter = read_sql(
            """
            SELECT brnd_name, gnrc_name, tot_clms, tot_drug_cst, cost_per_claim, opioid_drug_flag
            FROM mart_part_d_geo_drug
            WHERE prscrbr_geo_lvl = 'National' AND tot_clms >= 10000
            """
        )
        fig = px.scatter(
            scatter,
            x="tot_clms",
            y="cost_per_claim",
            size="tot_drug_cst",
            color="opioid_drug_flag",
            hover_name="brnd_name",
            hover_data=["gnrc_name"],
            log_x=True,
            log_y=True,
            color_discrete_map={"Y": RED, "N": TEAL, "": "#8CA0AE"},
            labels={"tot_clms": "Claims (log scale)", "cost_per_claim": "Cost per claim (log scale)", "opioid_drug_flag": "Opioid"},
            title="Utilization and cost per claim",
        )
        fig.update_layout(height=560)
        show_chart(fig)

    display = drugs.rename(
        columns={
            "brnd_name": "Brand",
            "gnrc_name": "Generic name",
            "tot_clms": "Claims",
            "tot_drug_cst": "Total drug cost",
            "cost_per_claim": "Cost per claim",
            "opioid_drug_flag": "Opioid flag",
        }
    )
    st.dataframe(
        display[["Brand", "Generic name", "Claims", "Total drug cost", "Cost per claim", "Opioid flag"]],
        width="stretch",
        hide_index=True,
        column_config={
            "Claims": st.column_config.NumberColumn(format="%,.0f"),
            "Total drug cost": st.column_config.NumberColumn(format="$%,.0f"),
            "Cost per claim": st.column_config.NumberColumn(format="$%,.2f"),
        },
    )

elif page == "State Comparison":
    st.title("State Comparison")
    states = state_summary()
    metric_labels = {
        "total_drug_cost": "Total drug cost",
        "total_claims": "Total claims",
        "cost_per_claim": "Cost per claim",
        "opioid_cost_share": "Opioid cost share",
    }
    metric = st.selectbox("Map metric", list(metric_labels), format_func=metric_labels.get)
    map_values = states[metric] * 100 if metric.endswith("_share") else states[metric]
    colorbar_title = metric_labels[metric] + (" (%)" if metric.endswith("_share") else "")
    fig = go.Figure(
        go.Choropleth(
            locations=states["state_code"],
            z=map_values,
            locationmode="USA-states",
            colorscale=[[0, "#DCEAF3"], [0.5, BLUE], [1, NAVY]],
            colorbar_title=colorbar_title,
            text=states["state_name"],
            hovertemplate="%{text}<br>%{z:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(geo_scope="usa", height=540, margin=dict(l=0, r=0, t=15, b=0))
    show_chart(fig)

    table = states.rename(
        columns={
            "state_code": "State",
            "total_claims": "Claims",
            "total_drug_cost": "Total drug cost",
            "cost_per_claim": "Cost per claim",
            "opioid_claim_share": "Opioid claim share",
            "opioid_cost_share": "Opioid cost share",
        }
    )
    table["Opioid claim share"] = table["Opioid claim share"] * 100
    table["Opioid cost share"] = table["Opioid cost share"] * 100
    st.dataframe(
        table[["State", "Claims", "Total drug cost", "Cost per claim", "Opioid claim share", "Opioid cost share"]],
        width="stretch",
        hide_index=True,
        column_config={
            "Claims": st.column_config.NumberColumn(format="%,.0f"),
            "Total drug cost": st.column_config.NumberColumn(format="$%,.0f"),
            "Cost per claim": st.column_config.NumberColumn(format="$%,.2f"),
            "Opioid claim share": st.column_config.NumberColumn(format="%.2f%%"),
            "Opioid cost share": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

else:
    st.title("Data Quality & Methodology")
    checks = quality_results()
    passed = int((checks.status == "PASS").sum())
    st.metric("Quality checks passed", f"{passed} of {len(checks)}")
    st.dataframe(checks, width="stretch", hide_index=True)

    st.subheader("Published source")
    st.markdown(f"[CMS Medicare Part D Prescribers — by Geography and Drug]({DATASET_PAGE})")
    st.write(f"Data year: {DATA_YEAR}. Publisher: Centers for Medicare & Medicaid Services.")
    st.subheader("Interpretation limits")
    st.write(
        "This public-use file is aggregated by geography and drug. It does not contain patient-level claims, "
        "diagnoses, adherence measures, plan-paid amounts, or causal evidence. Beneficiary counts can be suppressed "
        "and must not be summed across drugs as a count of unique people."
    )
