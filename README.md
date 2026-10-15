# Customer Shopping Behavior Analytics

An end-to-end analytics project that uses Python, SQL, Streamlit, and Power BI to answer business questions about customer purchasing behavior.

## Objective
Clean and analyze retail shopping data to understand what drives revenue, how promotions and subscriptions affect spending, and which customer segments are worth targeting.

## Dataset
- **File:** `shopping.csv`
- **Size:** 3,900 customers, 18 columns, no missing values
- **Grain:** one row per customer, one purchase each (no date or transaction ID, so no time-series or fraud analysis)
- **Key fields:** Purchase Amount (USD), Category, Item Purchased, Season, Location, Review Rating, Subscription Status, Discount Applied, Promo Code Used, Previous Purchases, Frequency of Purchases

## Business Questions
1. Which categories, items, and states drive the most revenue?
2. How does season affect what people buy and spend?
3. Do discounts and promo codes increase spend?
4. Are subscribers more valuable than non-subscribers?
5. Who are the main customer segments, and which are worth targeting?
6. Which products have low ratings?
7. Do shipping type or payment method relate to spend or satisfaction?

## Tools
Python (pandas, scikit-learn, scipy, plotly) | SQL | Streamlit | Power BI | VS Code | Git

## Project Structure
```
Customer_Shopping_Analysis/
├── data/
│   ├── raw/                # original CSV (untouched)
│   └── processed/          # cleaned data with engineered features
├── notebooks/
│   ├── 01_cleaning_eda.ipynb
│   └── 02_segmentation_testing.ipynb
├── sql/                    # one query file per business question
├── app/
│   └── streamlit_app.py
├── powerbi/
├── requirements.txt
└── README.md
```

## Setup
```bash
python -m venv cust
cust\Scripts\activate        # Windows
pip install -r requirements.txt
```
Place the dataset in `data/raw/`, then run the notebooks in order.

## Status
- [ ] Notebook 1:
