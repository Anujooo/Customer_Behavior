# Customer Shopping Behavior Analytics

An end-to-end analytics project that uses Python, SQL (SQLite), and Streamlit to answer business questions about customer purchasing behavior: what drives revenue, whether discounts and subscriptions raise spend, and which customer segments matter most.

## Objective
Clean and analyze retail shopping data to understand what drives revenue, how promotions and subscriptions affect spending, and which customer segments are worth targeting.

## Dataset
- **Source file:** `shopping.csv` (retail customer purchases)
- **Size:** 3,900 customers, 18 columns, no missing values or duplicates
- **Grain:** one row per customer, one purchase each. There is no date or transaction ID, so there is no time-series or fraud analysis.
- **Key fields:** Purchase Amount (USD), Category, Item Purchased, Season, Location, Review Rating, Subscription Status, Discount Applied, Promo Code Used, Previous Purchases, Frequency of Purchases
- **Processed files:** `shopping_clean.csv` (23 columns, after cleaning and feature engineering) and `shopping_segmented.csv` (24 columns, with the K-Means `segment` column)

## Business Questions
1. Which categories, items, and states drive the most revenue?
2. How does season affect what people buy and spend?
3. Do discounts and promo codes increase spend?
4. Are subscribers more valuable than non-subscribers?
5. Who are the main customer segments, and which are worth targeting?
6. Which products have low ratings?
7. Do shipping type or payment method relate to spend or satisfaction?

## Approach
1. **Cleaning and EDA (Python):** standardised column names, merged duplicate frequency labels, created age groups and spend buckets, and explored revenue, products, seasons, and ratings.
2. **SQL analysis (SQLite):** one query file per business question, using GROUP BY, CTEs, window functions, CASE WHEN, CROSS JOIN, and UNION ALL.
3. **Statistical testing (SciPy):** Welch t-tests, Mann-Whitney U, ANOVA, and Kruskal-Wallis, with a Bonferroni correction across 19 tests.
4. **Segmentation (Scikit-learn):** K-Means on age, spend, rating, and previous purchases, with k chosen using elbow and silhouette scores.
5. **Dashboard (Streamlit):** interactive app for stakeholders *(in progress)*.

## Key Findings
- **Revenue comes from order volume, not price.** Clothing is about 45% of revenue, followed by Accessories (32%), Footwear (16%), and Outerwear (8%). Average order value is about $57-$60 in every category.
- **Season has only a small effect.** Fall has the highest average order ($61.56) and Summer the lowest ($58.41). The difference is statistically weak and does not survive the multiple-testing correction.
- **Discounts and subscriptions do not raise spend per order.** Among men (the only group offered them), spend is $59.28 with a discount vs. $59.98 without (p = 0.47), and $59.49 for subscribers vs. $59.57 for non-subscribers (p = 0.94).
- **Data structure issue:** all subscribers and all discount/promo users are male, and the discount and promo columns are identical in every row. Comparisons were therefore run within men only.
- **Customer segments** (K-Means, k = 4):

| Segment | Customers | Avg age | Avg spend | Avg rating | Revenue share |
|---|---|---|---|---|---|
| Older High Spenders | 966 | 56 | $82.08 | 3.96 | 34.0% |
| Young At-Risk (Low Rating) | 986 | 33 | $64.76 | 3.09 | 27.4% |
| Young Satisfied Buyers | 969 | 31 | $54.86 | 4.43 | 22.8% |
| Older Low Spenders | 979 | 56 | $37.57 | 3.54 | 15.8% |

## Recommendations
- Protect the Older High Spenders: 25% of customers, 34% of revenue.
- Investigate why the Young At-Risk segment spends above average but gives the lowest ratings.
- Upsell the Young Satisfied Buyers, and bundle or cross-sell for the Older Low Spenders.
- Run a controlled A/B test before spending more on discounts, since they show no spend lift in this data.

## Limitations
- One purchase per customer and no dates, so repeat behavior, retention, and trends cannot be measured.
- Revenue means recorded sales, not profit. There is no cost or margin data, and it is unclear whether amounts are before or after discounts.
- Silhouette scores are low, so the segments are a practical partition of one continuous customer base, not distinct natural clusters.
- Near-uniform results suggest the dataset may be synthetic, so findings are illustrative.

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
- [ ] Streamlit dashboard and deployment

## Author
Anuj Sharma | Data Analyst
