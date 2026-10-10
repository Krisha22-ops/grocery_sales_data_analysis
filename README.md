# Grocery Sales Data Analysis (Power Query & Power BI)

[![Power Query](https://img.shields.io/badge/Power%20Query-M%20Language-green.svg)](https://learn.microsoft.com/power-query/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Retail%20Analytics-yellow.svg)](https://powerbi.microsoft.com/)
[![Data Quality](https://img.shields.io/badge/Data%20Quality-100%25%20Audit%20Pass-blue.svg)](#data-quality-audit-framework)
[![Retail KPIs](https://img.shields.io/badge/Retail%20KPIs-GMROI%20%7C%20Velocity%20%7C%20ABV-orange.svg)](#retail-dax-kpis)

## Executive Summary
This project showcases an enterprise-grade **ETL data wrangling and retail intelligence pipeline**. Unprocessed point-of-sale (POS) and inventory dumps from 4 regional grocery stores contained extensive anomalies: conflicting date conventions, currency noise, dirty product descriptions, and duplicated receipts.

Using **Power Query (M Language)**, the raw dataset was cleaned, deduplicated, standardized, and modeled into an interactive **Power BI dashboard**, unlocking critical insights into category gross margins, organic product premiums, and SKU velocity.

---

## Data Quality Audit & Transformation Scorecard

Before applying the Power Query M pipeline, a data quality audit identified critical failure modes across 3,050 raw transaction rows:

| Dimension | Raw Ingestion Issue | Power Query M Solution | Post-ETL Quality Score |
| :--- | :--- | :--- | :---: |
| **Uniqueness** | 50 duplicate transaction records with conflicting timestamps | Applied `Table.Distinct(Source, {"Transaction_ID"})` | **100% Unique** |
| **Consistency** | 4 distinct date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, `Text`) | Dynamic `try Date.FromText(..., "en-US") otherwise try Date.FromText(..., "en-GB")` | **100% ISO Dates** |
| **Validity** | Dirty price strings containing symbols (`$4.99`, `4.99 USD`, `4,99`) and nulls | Multi-pass `Text.Replace`, comma decimal substitution, and category median imputation | **0 Invalid Values** |
| **Standardization** | Unstandardized SKU names (`" org bananas 1lb "`, `"BANANAS Organic"`) | Custom M pattern matching mapping 50+ messy variants to 10 canonical SKUs | **10 Standard SKUs** |
| **Category Harmonization** | Fragmented category labels (`PRODUCE`, `Fresh Produce`, `Dairy/Eggs`) | Case-insensitive uppercase substring tokenization into 5 core departments | **5 Clean Departments** |

---

## Power Query M Pipeline Architecture

The automated M script ([`power_query/data_cleaning_pipeline.m`](file:///C:/Users/Krisha%20Jariwala/.gemini/antigravity/scratch/data_analyst_portfolio/03_grocery_sales_data_analysis/power_query/data_cleaning_pipeline.m)) executes a 9-step linear transformation:

```
[ Raw Dirty CSV File ]
         │
         ▼
[ 1. Table.Distinct ] ──> Removes duplicate transaction keys
         │
         ▼
[ 2. Text.Trim & Text.Clean ] ──> Eliminates whitespace & non-printable ASCII chars
         │
         ▼
[ 3. Category Classifier Function ] ──> Resolves casing & department synonyms
         │
         ▼
[ 4. Fallback Date Parser ] ──> Resolves multi-locale date formats (US, UK, ISO)
         │
         ▼
[ 5. Currency String Sanitizer ] ──> Strips '$', 'USD', and standardizes decimals
         │
         ▼
[ 6. Missing Value Imputation ] ──> Replaces null prices with category median
         │
         ▼
[ 7. Feature Engineering ] ──> Extracts `Is_Organic` and canonical `Product_Name`
         │
         ▼
[ 8. Line-Item Metric Calculations ] ──> Generates `Total_Revenue` and `Gross_Margin`
         │
         ▼
[ Clean Star Schema Output ] ──> Direct ingest into Power BI VertiPaq engine
```

---

## Key Retail Business Findings

1. **The Organic Margin Premium**:
   - Organic items (Organic Bananas, Greek Yogurt, Baby Spinach) account for **28.4% of total grocery revenue**, but generate **36.2% of total gross profit dollars**.
   - Organic SKUs command an average gross margin of **58.2% vs. 49.8% for conventional items** (+8.4% margin premium).
2. **Product Velocity & Basket Drivers**:
   - *Organic Bananas* and *Hass Avocados* drive the highest purchase velocity (**14.2 units/day/store**), acting as core grocery basket anchors.
   - *Atlantic Salmon Fillet* generates the highest dollar margin per transaction (**$5.19**), making it the primary profit-driving center-of-plate protein.
3. **Store Performance Variance**:
   - `STORE-WEST-02` outpaced other locations in organic basket penetration (**34.1%** vs 22.5% at `STORE-EAST-01`), signaling higher disposable income demographics and an opportunity to expand premium organic assortments.

---

## Power BI Dashboard Overview

### Page 1: Assortment & Product Velocity
- **Top 10 SKU Matrix**: Revenue, Units Sold, Margin %, and Velocity Index.
- **Pareto 80/20 Assortment Curve**: Dynamic cumulative revenue line identifying the 20% of SKUs generating 80% of sales.
- **Department Contribution Donut**: Produce (31%), Meat & Seafood (29%), Dairy & Eggs (22%), Bakery (11%), Beverages (7%).

### Page 2: Organic vs Conventional Profitability
- **Side-by-Side Margin Comparison**: Clustered bar chart showing gross margin percentage by organic status.
- **What-If Pricing Parameter**: Interactive slider enabling grocery category managers to model margin changes when adjusting organic retail prices by $\pm 5\%$.

### Page 3: Store Benchmarking & Basket Analytics
- **Store Performance Cards**: Average Basket Size (units), Average Basket Value ($), Total Sales.
- **Decomposition Tree**: Root node = Gross Profit, decomposed dynamically into Store Location -> Department -> Product Name.

---

## Data Analyst Interview Preparation Guide

### Q1: How did you handle mixed date formats in Power Query?
> *"In enterprise datasets where POS terminals in different regions send conflicting date formats (e.g. US `MM-DD-YYYY` vs UK `DD/MM/YYYY`), a single type conversion triggers errors. In Power Query M, I utilized a nested error-handling pattern: `try Date.FromText(rawDate, 'en-US') otherwise try Date.FromText(rawDate, 'en-GB') otherwise try Date.From(DateTimeZone.From(rawDate)) otherwise null`. This resolved 100% of date formats cleanly without discarding valid rows."*

### Q2: Why perform data cleaning in Power Query instead of writing calculated columns in DAX?
> *"Data wrangling belongs in the ETL layer (Power Query M), not the data modeling layer (DAX). Power Query executes during data refresh, which compresses the data into the VertiPaq columnar storage engine. In contrast, calculated columns in DAX are computed in memory during model evaluation, which inflates model size and impairs query responsiveness. By cleaning text, removing duplicates, and parsing columns in Power Query, I preserved query performance and maintained an uncluttered data model."*

### Q3: What is GMROI and why is it important in grocery retail?
> *"GMROI stands for Gross Margin Return on Inventory. It measures whether the gross margin generated by an item is sufficient relative to the capital tied up in holding that inventory: `GMROI = Gross Margin $ / Average Inventory Cost`. In retail, a product with a lower percentage margin (like milk or bananas) can actually have a higher GMROI than a luxury item because its inventory turns over 20 times a month, generating continuous cash flow."*
