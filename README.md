# Customer Shopping Behavior Analytics

An end-to-end analytics project using **Python, SQL (SQLite), and Streamlit** to answer a practical retail question: *what drives revenue, do discounts and subscriptions actually raise spend, and which customer segments deserve the most attention?*

---

## Summary

- Revenue is driven by **order volume, not price**. Average order value is about $57-$60 in every category, so growth depends on getting more orders from the right customers.
- **Discounts, promo codes, and subscriptions show no lift in spend per order** in this data, so any further spend on them should be tested first.
- Four customer segments were identified. **Older High Spenders are 25% of customers but 34% of revenue** and are the group to protect.
- **Young At-Risk buyers** spend above average but give the lowest ratings, making them the biggest satisfaction problem to investigate.

---

## Objective

Clean and analyze retail shopping data to understand what drives revenue, how promotions and subscriptions affect spending, and which customer segments are worth targeting, then turn the results into specific business recommendations.

## Dataset

| Item | Detail |
|---|---|
| Source file | `shopping.csv` (retail customer purchases) |
| Size | 3,900 customers, 18 columns, no missing values or duplicates |
| Grain | One row per customer, one purchase each |
| Key fields | Purchase Amount (USD), Category, Item Purchased, Season, Location, Review Rating, Subscription Status, Discount Applied, Promo Code Used, Previous Purchases, Frequency of Purchases |
| Processed files | `shopping_clean.csv` (23 columns, after cleaning and feature engineering) and `shopping_segmented.csv` (24 columns, with the K-Means segment column) |

There is no date or transaction ID, so time-series and fraud analysis are out of scope.

## Business Questions

1. Which categories, items, and states drive the most revenue?
2. How does season affect what people buy and spend?
3. Do discounts and promo codes increase spend?
4. Are subscribers more valuable than non-subscribers?
5. Who are the main customer segments, and which are worth targeting?
6. Which products have low ratings?
7. Do shipping type or payment method relate to spend or satisfaction?

## Approach

| Stage | Tools | What was done |
|---|---|---|
| Cleaning and EDA | Python | Standardised column names, merged duplicate frequency labels, created age groups and spend buckets, explored revenue, products, seasons, and ratings |
| SQL analysis | SQLite | One query file per business question, using `GROUP BY`, CTEs, window functions, `CASE WHEN`, `CROSS JOIN`, and `UNION ALL` |
| Statistical testing | SciPy | Welch t-tests, Mann-Whitney U, ANOVA, and Kruskal-Wallis, with a Bonferroni correction across 19 tests |
| Segmentation | Scikit-learn | K-Means on age, spend, rating, and previous purchases, with k chosen using elbow and silhouette scores |
| Dashboard | Streamlit | Interactive app for stakeholders |

---

## Findings and Recommendations

### 1. Focus on order volume, not pricing, to grow revenue

**What the data shows:** Clothing generates about 45% of revenue, followed by Accessories (32%), Footwear (16%), and Outerwear (8%). Average order value is about $57-$60 in every category.

**Recommendation:** Since price per order barely differs by category, revenue growth should come from increasing the number of orders. Prioritise inventory, marketing, and placement for Clothing and Accessories (together about 77% of revenue), and treat Outerwear as a niche line unless there is a plan to grow its order volume.

### 2. Do not build strategy around seasonality

**What the data shows:** Fall has the highest average order ($61.56) and Summer the lowest ($58.41). The difference is statistically weak and does not survive the multiple-testing correction.

**Recommendation:** Treat season as a minor factor. Seasonal campaigns can still be used for merchandising reasons, but there is no evidence that they will change spend per order, so they should not be a major budget driver.

### 3. Test discounts before spending more on them

**What the data shows:** Among men (the only group offered discounts and subscriptions), spend is $59.28 with a discount vs. $59.98 without (p = 0.47). Subscribers spend $59.49 vs. $59.57 for non-subscribers (p = 0.94). Neither difference is meaningful.

**Recommendation:** Do not expand discount or subscription budgets on the basis of this data. Run a controlled A/B test with randomly assigned offers across all customer groups before committing more spend. Measure order frequency and retention as well as spend per order, since this dataset cannot show those.

### 4. Fix the data design before judging promotions

**What the data shows:** All subscribers and all discount/promo users are male, and the discount and promo columns are identical in every row. All comparisons were therefore made within men only.

**Recommendation:** Offer promotions and subscriptions to all genders, and track discount and promo code usage separately. Without this, the business cannot tell whether these tools work for women, or whether discounts and promo codes behave differently.

### 5. Protect the Older High Spenders

**What the data shows:** This segment is 966 customers (25%) producing 34% of revenue, with an average spend of $82.08 and a rating of 3.96.

**Recommendation:** Make this group the retention priority. Use loyalty perks, early access, and personal service rather than discounts, since discounts showed no spend lift. Monitor their ratings, since their satisfaction is good but not as high as the Young Satisfied Buyers.

### 6. Investigate the Young At-Risk segment

**What the data shows:** 986 customers (27.4% of revenue) with above-average spend ($64.76) but the lowest average rating (3.09).

**Recommendation:** Find out why this group is unhappy. Cross-check low-rated products from the ratings analysis, then run a short survey or review-text analysis. These customers already spend well, so fixing the cause of low ratings protects a large block of revenue.

### 7. Grow the two lower-value segments with different tactics

| Segment | Customers | Avg age | Avg spend | Avg rating | Revenue share | Recommended action |
|---|---|---|---|---|---|---|
| Older High Spenders | 966 | 56 | $82.08 | 3.96 | 34.0% | Protect and retain |
| Young At-Risk (Low Rating) | 986 | 33 | $64.76 | 3.09 | 27.4% | Diagnose and fix satisfaction |
| Young Satisfied Buyers | 969 | 31 | $54.86 | 4.43 | 22.8% | Upsell to raise order value |
| Older Low Spenders | 979 | 56 | $37.57 | 3.54 | 15.8% | Bundle and cross-sell |

**Recommendation:** Young Satisfied Buyers have the best ratings but lower spend, so they are the best candidates for upselling. Older Low Spenders have the lowest spend, so bundles and cross-sell offers are the most practical way to lift their order value.

### Suggested priority order

1. Retain the Older High Spenders (largest revenue share).
2. Diagnose the Young At-Risk satisfaction problem.
3. Run the discount and subscription A/B test before any new promotion spend.
4. Upsell Young Satisfied Buyers and bundle for Older Low Spenders.
5. Fix the data collection gaps (promotion tracking, dates, repeat purchases).

---

## Dashboard

The Streamlit app (`app/streamlit_app.py`) lets stakeholders explore revenue by category, season, and location, compare discount and subscription groups, and view the customer segments.

Run it locally:

```bash
streamlit run app/streamlit_app.py
```

## Limitations

- **One purchase per customer and no dates**, so repeat behavior, retention, and trends cannot be measured.
- **Revenue means recorded sales, not profit.** There is no cost or margin data, and it is unclear whether amounts are before or after discounts.
- **Silhouette scores are low**, so the segments are a practical partition of one continuous customer base, not distinct natural clusters.
- **Near-uniform results suggest the dataset may be synthetic**, so the findings are illustrative rather than a real business conclusion.

## Tools

Python (pandas, NumPy, SciPy, scikit-learn, matplotlib, seaborn, Plotly) | SQL (SQLite) | Streamlit | VS Code | Git

## Project Structure

```
Customer_Behavior/
├── data/
│   ├── raw/                 # original CSV (untouched)
│   └── processed/           # shopping_clean.csv, shopping_segmented.csv
├── notebooks/
│   ├── 01_cleaning_eda.ipynb
│   └── 02_segmentation_testing.ipynb
├── sql/                     # one query file per business question
├── app/
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv cust
source cust/Scripts/activate     # Git Bash on Windows
cust\Scripts\activate            # Windows Command Prompt
pip install -r requirements.txt
```

Place the dataset in `data/raw/`, then run the notebooks in order (`01`, then `02`).

## Running the SQL

Load `data/processed/shopping_segmented.csv` into a SQLite database as a table named `customers` (using DB Browser for SQLite or the notebook), then run the files in `sql/` in order.

## Status

- [x] Notebook 1: cleaning and EDA
- [x] Notebook 2: statistical tests and segmentation
- [x] SQL queries
- [x] Streamlit dashboard and deployment

## Author

**Anuj Sharma** | Data Analyst
