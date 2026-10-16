import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Customer Shopping Behavior Analytics",
    page_icon="🛍️",
    layout="wide",
)

SEGMENT_ORDER = [
    "Older High Spenders",
    "Young At-Risk (Low Rating)",
    "Young Satisfied Buyers",
    "Older Low Spenders",
]
SEGMENT_COLORS = {
    "Older High Spenders": "#1f77b4",
    "Young At-Risk (Low Rating)": "#d62728",
    "Young Satisfied Buyers": "#2ca02c",
    "Older Low Spenders": "#ff7f0e",
}
SEASON_ORDER = ["Spring", "Summer", "Fall", "Winter"]
AGE_ORDER = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]

BASE = Path(__file__).resolve().parent
CANDIDATES = [
    BASE / "shopping_segmented.csv",
    BASE / "data" / "shopping_segmented.csv",
    BASE / "data" / "processed" / "shopping_segmented.csv",
]


# ---------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------
@st.cache_data
def load_csv(source):
    return pd.read_csv(source)


def get_data():
    for path in CANDIDATES:
        if path.exists():
            return load_csv(path)
    st.warning("Couldn't find `shopping_segmented.csv` next to dashboard.py. Upload it below.")
    uploaded = st.file_uploader("Upload shopping_segmented.csv", type="csv")
    if uploaded is None:
        st.stop()
    return load_csv(uploaded)


df = get_data()

required = {
    "customer_id", "age", "gender", "item_purchased", "category",
    "purchase_amount_usd", "location", "season", "review_rating",
    "subscription_status", "shipping_type", "discount_applied",
    "promo_code_used", "previous_purchases", "payment_method",
    "frequency_of_purchases", "age_group", "segment",
}
missing = required - set(df.columns)
if missing:
    st.error(f"CSV is missing expected columns: {sorted(missing)}")
    st.stop()

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")


def multiselect_filter(label, column, order=None):
    options = sorted(df[column].dropna().unique())
    if order:
        options = [o for o in order if o in options]
    return st.sidebar.multiselect(label, options, default=options)


sel_season = multiselect_filter("Season", "season", SEASON_ORDER)
sel_category = multiselect_filter("Category", "category")
sel_gender = multiselect_filter("Gender", "gender")
sel_age = multiselect_filter("Age group", "age_group", AGE_ORDER)
sel_segment = multiselect_filter("Segment", "segment", SEGMENT_ORDER)

fdf = df[
    df["season"].isin(sel_season)
    & df["category"].isin(sel_category)
    & df["gender"].isin(sel_gender)
    & df["age_group"].isin(sel_age)
    & df["segment"].isin(sel_segment)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(fdf):,} of {len(df):,} customers")

# ---------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------
st.title("🛍️ Customer Shopping Behavior Analytics")
st.caption(
    "One row per customer, one purchase each. 'Revenue' = recorded sales, not profit. "
    "No dates in the data, so no trend or retention analysis."
)

if fdf.empty:
    st.warning("No customers match the current filters.")
    st.stop()

total_rev = fdf["purchase_amount_usd"].sum()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{len(fdf):,}")
k2.metric("Total revenue", f"${total_rev:,.0f}")
k3.metric("Avg order value", f"${fdf['purchase_amount_usd'].mean():.2f}")
k4.metric("Avg review rating", f"{fdf['review_rating'].mean():.2f}")
k5.metric("Avg previous purchases", f"{fdf['previous_purchases'].mean():.1f}")

tab_over, tab_season, tab_promo, tab_seg, tab_prod, tab_ship, tab_data = st.tabs([
    "Revenue drivers",
    "Seasonality",
    "Discounts & subscriptions",
    "Customer segments",
    "Products & ratings",
    "Shipping & payment",
    "Data",
])

# ---------------------------------------------------------------
# Tab 1: Revenue drivers
# ---------------------------------------------------------------
with tab_over:
    c1, c2 = st.columns(2)

    cat = (
        fdf.groupby("category")
        .agg(revenue=("purchase_amount_usd", "sum"),
             orders=("customer_id", "count"),
             aov=("purchase_amount_usd", "mean"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    cat["share"] = cat["revenue"] / cat["revenue"].sum()

    with c1:
        st.subheader("Revenue by category")
        fig = px.bar(cat, x="category", y="revenue", text=cat["share"].map("{:.0%}".format),
                     labels={"revenue": "Revenue (USD)", "category": ""})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Average order value by category")
        fig = px.bar(cat, x="category", y="aov", text=cat["aov"].map("${:.2f}".format),
                     labels={"aov": "Avg order value (USD)", "category": ""})
        fig.update_traces(textposition="outside")
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("AOV is nearly flat across categories, so revenue differences come from order volume.")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top 10 items by revenue")
        items = (
            fdf.groupby("item_purchased")["purchase_amount_usd"].sum()
            .sort_values(ascending=False).head(10).reset_index()
            .sort_values("purchase_amount_usd")
        )
        fig = px.bar(items, x="purchase_amount_usd", y="item_purchased", orientation="h",
                     labels={"purchase_amount_usd": "Revenue (USD)", "item_purchased": ""})
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Top 10 states by revenue")
        states = (
            fdf.groupby("location")["purchase_amount_usd"].sum()
            .sort_values(ascending=False).head(10).reset_index()
            .sort_values("purchase_amount_usd")
        )
        fig = px.bar(states, x="purchase_amount_usd", y="location", orientation="h",
                     labels={"purchase_amount_usd": "Revenue (USD)", "location": ""})
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# Tab 2: Seasonality
# ---------------------------------------------------------------
with tab_season:
    c1, c2 = st.columns(2)
    season = (
        fdf.groupby("season")
        .agg(avg_order=("purchase_amount_usd", "mean"),
             revenue=("purchase_amount_usd", "sum"),
             orders=("customer_id", "count"))
        .reindex([s for s in SEASON_ORDER if s in fdf["season"].unique()])
        .reset_index()
    )
    with c1:
        st.subheader("Average order value by season")
        fig = px.bar(season, x="season", y="avg_order", text=season["avg_order"].map("${:.2f}".format),
                     labels={"avg_order": "Avg order value (USD)", "season": ""})
        fig.update_traces(textposition="outside")
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Season has only a small effect on spend per order (not significant after multiple-testing correction in your analysis).")

    with c2:
        st.subheader("Revenue: season × category")
        pivot = fdf.pivot_table(index="category", columns="season",
                                values="purchase_amount_usd", aggfunc="sum").fillna(0)
        pivot = pivot[[s for s in SEASON_ORDER if s in pivot.columns]]
        fig = px.imshow(pivot, text_auto=",.0f", aspect="auto", color_continuous_scale="Blues",
                        labels={"color": "Revenue"})
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# Tab 3: Discounts & subscriptions (men only)
# ---------------------------------------------------------------
with tab_promo:
    st.info(
        "Data structure issue: all subscribers and all discount/promo users are male, and the "
        "discount and promo columns are identical. Comparisons below use men only."
    )
    men = fdf[fdf["gender"] == "Male"]

    if men.empty:
        st.warning("No male customers in the current filter selection.")
    else:
        try:
            from scipy import stats
            have_scipy = True
        except ImportError:
            have_scipy = False

        def compare(col, title):
            g = (
                men.groupby(col)["purchase_amount_usd"]
                .agg(["mean", "count"]).reset_index()
            )
            fig = px.bar(g, x=col, y="mean", text=g["mean"].map("${:.2f}".format),
                         labels={"mean": "Avg order value (USD)", col: ""}, title=title)
            fig.update_traces(textposition="outside")
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig, use_container_width=True)

            yes = men.loc[men[col] == "Yes", "purchase_amount_usd"]
            no = men.loc[men[col] == "No", "purchase_amount_usd"]
            if have_scipy and len(yes) > 1 and len(no) > 1:
                t, p = stats.ttest_ind(yes, no, equal_var=False)
                st.caption(
                    f"Yes: ${yes.mean():.2f} (n={len(yes):,}) vs No: ${no.mean():.2f} (n={len(no):,}) "
                    f"| Welch t-test p = {p:.3f}"
                )
            else:
                st.caption(f"Yes n={len(yes):,}, No n={len(no):,}")

        c1, c2 = st.columns(2)
        with c1:
            compare("discount_applied", "Discount applied vs not (men)")
        with c2:
            compare("subscription_status", "Subscriber vs non-subscriber (men)")

        st.caption("No meaningful spend lift from discounts or subscriptions. Run a controlled A/B test before spending more on discounts.")

# ---------------------------------------------------------------
# Tab 4: Segments
# ---------------------------------------------------------------
with tab_seg:
    seg = (
        fdf.groupby("segment")
        .agg(customers=("customer_id", "count"),
             avg_age=("age", "mean"),
             avg_spend=("purchase_amount_usd", "mean"),
             avg_rating=("review_rating", "mean"),
             revenue=("purchase_amount_usd", "sum"))
        .reset_index()
    )
    seg["revenue_share"] = seg["revenue"] / seg["revenue"].sum()
    seg["segment"] = pd.Categorical(seg["segment"], categories=SEGMENT_ORDER, ordered=True)
    seg = seg.sort_values("segment")

    st.subheader("Segment summary")
    st.dataframe(
        seg.assign(
            avg_age=seg["avg_age"].round(0).astype(int),
            avg_spend=seg["avg_spend"].map("${:.2f}".format),
            avg_rating=seg["avg_rating"].round(2),
            revenue=seg["revenue"].map("${:,.0f}".format),
            revenue_share=seg["revenue_share"].map("{:.1%}".format),
        ).rename(columns={
            "segment": "Segment", "customers": "Customers", "avg_age": "Avg age",
            "avg_spend": "Avg spend", "avg_rating": "Avg rating",
            "revenue": "Revenue", "revenue_share": "Revenue share",
        }),
        use_container_width=True, hide_index=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue share by segment")
        fig = px.pie(seg, names="segment", values="revenue", hole=0.45,
                     color="segment", color_discrete_map=SEGMENT_COLORS,
                     category_orders={"segment": SEGMENT_ORDER})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Avg spend vs avg rating")
        fig = px.scatter(seg, x="avg_rating", y="avg_spend", size="customers",
                         color="segment", color_discrete_map=SEGMENT_COLORS,
                         labels={"avg_rating": "Avg rating", "avg_spend": "Avg spend (USD)"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customers: age vs purchase amount")
    fig = px.scatter(fdf, x="age", y="purchase_amount_usd", color="segment",
                     color_discrete_map=SEGMENT_COLORS, opacity=0.6,
                     category_orders={"segment": SEGMENT_ORDER},
                     labels={"age": "Age", "purchase_amount_usd": "Purchase amount (USD)"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Silhouette scores are low: segments are a practical partition of one continuous customer base, not distinct natural clusters.")

# ---------------------------------------------------------------
# Tab 5: Products & ratings
# ---------------------------------------------------------------
with tab_prod:
    c1, c2 = st.columns(2)
    items = (
        fdf.groupby("item_purchased")
        .agg(avg_rating=("review_rating", "mean"), orders=("customer_id", "count"))
        .reset_index()
    )
    with c1:
        st.subheader("10 lowest-rated items")
        low = items.sort_values("avg_rating").head(10).sort_values("avg_rating", ascending=False)
        fig = px.bar(low, x="avg_rating", y="item_purchased", orientation="h",
                     text=low["avg_rating"].round(2),
                     labels={"avg_rating": "Avg rating", "item_purchased": ""})
        fig.update_xaxes(range=[max(0, low["avg_rating"].min() - 0.3), 5])
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Axis is zoomed in: differences between items are small.")

    with c2:
        st.subheader("Rating distribution")
        fig = px.histogram(fdf, x="review_rating", nbins=20,
                           labels={"review_rating": "Review rating"})
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# Tab 6: Shipping & payment
# ---------------------------------------------------------------
with tab_ship:
    c1, c2 = st.columns(2)

    def by_col(col, title, container):
        g = (
            fdf.groupby(col)
            .agg(avg_spend=("purchase_amount_usd", "mean"),
                 avg_rating=("review_rating", "mean"),
                 orders=("customer_id", "count"))
            .reset_index().sort_values("avg_spend", ascending=False)
        )
        with container:
            st.subheader(title)
            fig = px.bar(g, x=col, y="avg_spend", text=g["avg_spend"].map("${:.2f}".format),
                         labels={"avg_spend": "Avg order value (USD)", col: ""})
            fig.update_traces(textposition="outside")
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(
                g.assign(avg_spend=g["avg_spend"].round(2), avg_rating=g["avg_rating"].round(2)),
                use_container_width=True, hide_index=True,
            )

    by_col("shipping_type", "By shipping type", c1)
    by_col("payment_method", "By payment method", c2)

    st.subheader("Purchase frequency")
    freq = fdf["frequency_of_purchases"].value_counts().reset_index()
    freq.columns = ["frequency", "customers"]
    fig = px.bar(freq, x="frequency", y="customers", labels={"frequency": "", "customers": "Customers"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# Tab 7: Data
# ---------------------------------------------------------------
with tab_data:
    st.subheader("Filtered data")
    st.dataframe(fdf, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered CSV",
        fdf.to_csv(index=False).encode("utf-8"),
        file_name="shopping_filtered.csv",
        mime="text/csv",
    )