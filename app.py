import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Executive Business Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clean_dataset.csv")
    df["created_at"] = pd.to_datetime(df["created_at"])

    return df


df = load_data()

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Executive Business Dashboard")
st.markdown(
    "Interactive business performance dashboard built using "
    "**Python, Pandas, Streamlit and Plotly**."
)

st.divider()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Dashboard Filters")

year_options = sorted(df["year"].dropna().unique())

selected_year = st.sidebar.multiselect(
    "Select Year",
    options=year_options,
    default=year_options
)

month_options = sorted(df["month_name"].dropna().unique())

selected_month = st.sidebar.multiselect(
    "Select Month",
    options=month_options,
    default=month_options
)

filtered_df = df[
    (df["year"].isin(selected_year)) &
    (df["month_name"].isin(selected_month))
].copy()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_revenue = filtered_df["revenue_usd"].sum()
total_profit = filtered_df["profit_usd"].sum()
total_orders = filtered_df["order_id"].nunique()
total_units = filtered_df["items_purchased"].sum()

aov = total_revenue / total_orders if total_orders else 0
profit_margin = (
    (total_profit / total_revenue) * 100
    if total_revenue else 0
)

# -----------------------------
# KPI CARDS
# -----------------------------
st.subheader("Executive KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "📦 Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "🛒 Average Order Value",
    f"${aov:,.2f}"
)

col4.metric(
    "📈 Total Profit",
    f"${total_profit:,.2f}"
)

col5.metric(
    "💹 Profit Margin",
    f"{profit_margin:.2f}%"
)

st.divider()

# -----------------------------
# MONTHLY TREND
# -----------------------------
st.subheader("📈 Revenue & Profit Trend")

monthly = (
    filtered_df
    .groupby(["year", "month"], as_index=False)
    .agg(
        Revenue=("revenue_usd", "sum"),
        Profit=("profit_usd", "sum")
    )
)

monthly["Period"] = (
    monthly["year"].astype(str)
    + "-"
    + monthly["month"].astype(str).str.zfill(2)
)

fig_trend = px.area(
    monthly,
    x="Period",
    y=["Revenue", "Profit"],
    title="Monthly Revenue and Profit Trend",
    markers=True
)

fig_trend.update_layout(
    xaxis_title="Period",
    yaxis_title="USD",
    legend_title="Metric",
    hovermode="x unified"
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)

# -----------------------------
# REVENUE & PROFIT ANALYSIS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Revenue Distribution")

    fig_revenue = px.histogram(
        filtered_df,
        x="revenue_usd",
        nbins=30,
        title="Revenue Distribution"
    )

    fig_revenue.update_layout(
        xaxis_title="Revenue (USD)",
        yaxis_title="Number of Orders"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

with col2:
    st.subheader("📊 Profit Distribution")

    fig_profit = px.histogram(
        filtered_df,
        x="profit_usd",
        nbins=30,
        title="Profit Distribution"
    )

    fig_profit.update_layout(
        xaxis_title="Profit (USD)",
        yaxis_title="Number of Orders"
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )

# -----------------------------
# PRICE VS REVENUE
# -----------------------------
st.subheader("🔗 Price vs Revenue Relationship")

fig_scatter = px.scatter(
    filtered_df.sample(
        min(3000, len(filtered_df)),
        random_state=42
    ),
    x="price_usd",
    y="revenue_usd",
    size="items_purchased",
    hover_data=[
        "order_id",
        "user_id",
        "profit_usd"
    ],
    title="Product Price vs Order Revenue",
    opacity=0.6
)

fig_scatter.update_layout(
    xaxis_title="Product Price (USD)",
    yaxis_title="Revenue (USD)"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# -----------------------------
# PROFIT MARGIN
# -----------------------------
st.subheader("💹 Profit Margin Analysis")

margin_summary = (
    filtered_df
    .groupby("month_name", as_index=False)
    .agg(
        Average_Profit_Margin=("profit_margin_pct", "mean")
    )
)

fig_margin = px.bar(
    margin_summary,
    x="month_name",
    y="Average_Profit_Margin",
    title="Average Profit Margin by Month",
    text_auto=".2f"
)

fig_margin.update_layout(
    xaxis_title="Month",
    yaxis_title="Profit Margin (%)"
)

st.plotly_chart(
    fig_margin,
    use_container_width=True
)

# -----------------------------
# TOP PRODUCTS
# -----------------------------
st.subheader("🏆 Product Performance")

product_summary = (
    filtered_df
    .groupby("primary_product_id", as_index=False)
    .agg(
        Revenue=("revenue_usd", "sum"),
        Profit=("profit_usd", "sum"),
        Orders=("order_id", "nunique"),
        Units=("items_purchased", "sum")
    )
    .sort_values("Revenue", ascending=False)
)

fig_products = px.bar(
    product_summary.head(10),
    x="primary_product_id",
    y="Revenue",
    title="Top 10 Products by Revenue",
    text_auto=".2s"
)

fig_products.update_layout(
    xaxis_title="Product ID",
    yaxis_title="Revenue (USD)"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)

# -----------------------------
# DATA SUMMARY
# -----------------------------
with st.expander("📋 View Filtered Data"):

    st.write(
        f"Showing **{len(filtered_df):,} records**"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
    "Task 5 — Interactive Dashboard & KPI Visualizations | "
    "Built with Python, Pandas, Streamlit & Plotly"
)