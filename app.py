
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Workora Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Interactive Business Intelligence Dashboard")
st.caption("Educational project using synthetic data")

folder = Path(__file__).parent

web = pd.read_csv(folder / "web_traffic.csv")
churn = pd.read_csv(folder / "customer_churn.csv")
regional = pd.read_csv(folder / "regional_market.csv")
checkout = pd.read_csv(folder / "checkout_ab_test.csv")

st.sidebar.header("Dashboard Filters")

# Region filter
if "Region" in churn.columns:
    regions = sorted(churn["Region"].dropna().astype(str).unique())
    selected = st.sidebar.multiselect(
        "Customer Region", regions, default=regions
    )
    churn = churn[churn["Region"].astype(str).isin(selected)]

# KPI calculations
churn_rate = 0
if "Churn" in churn.columns and len(churn) > 0:
    churn_rate = (
        churn["Churn"].astype(str).str.lower().eq("yes").mean() * 100
    )

conversion_rate = 0
avg_order_value = 0

if "Converted" in checkout.columns and len(checkout) > 0:
    converted = checkout["Converted"].astype(str).str.lower().eq("yes")
    conversion_rate = converted.mean() * 100

    if "OrderValueINR" in checkout.columns and converted.any():
        values = pd.to_numeric(
            checkout.loc[converted, "OrderValueINR"], errors="coerce"
        )
        avg_order_value = values.mean()

sessions = len(web)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Web Sessions", f"{sessions:,}")
c2.metric("Customer Churn", f"{churn_rate:.2f}%")
c3.metric("Checkout Conversion", f"{conversion_rate:.2f}%")
c4.metric("Avg. Order Value", f"₹{avg_order_value:,.2f}")

st.info(
    "Datasets are synthetic and intended for learning. "
    "Revenue and active-user totals are not reported unless supported by data."
)

# Traffic source chart
if "Source" in web.columns:
    st.subheader("Sessions by Traffic Source")
    source_counts = web["Source"].value_counts().reset_index()
    source_counts.columns = ["Source", "Sessions"]
    fig = px.bar(source_counts, x="Source", y="Sessions")
    st.plotly_chart(fig, use_container_width=True)

# Regional demand chart
if {"City", "MonthlySearchDemand"}.issubset(regional.columns):
    st.subheader("Regional Search Demand")
    demand = regional.groupby(
        "City", as_index=False
    )["MonthlySearchDemand"].sum()
    demand = demand.sort_values(
        "MonthlySearchDemand", ascending=False
    ).head(15)
    fig = px.bar(
        demand, x="City", y="MonthlySearchDemand",
        title="Top Cities by Search Demand"
    )
    st.plotly_chart(fig, use_container_width=True)

# Checkout A/B test
if {"Variant", "Converted"}.issubset(checkout.columns):
    st.subheader("Checkout A/B Test")
    checkout["ConvertedFlag"] = (
        checkout["Converted"].astype(str).str.lower().eq("yes").astype(int)
    )
    ab = checkout.groupby("Variant", as_index=False).agg(
        Visitors=("VisitorID", "nunique"),
        Conversion=("ConvertedFlag", "mean")
    )
    ab["Conversion Rate (%)"] = ab["Conversion"] * 100
    fig = px.bar(
        ab, x="Variant", y="Conversion Rate (%)",
        title="Conversion Rate by Variant"
    )
    st.plotly_chart(fig, use_container_width=True)

st.caption("Demo dashboard — not actual Workora business results.")
