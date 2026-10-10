# Grocery Retail Sales Analytics - Power BI Dashboard Implementation Guide

This guide explains how to view, edit, and publish the **FreshMart FMCG Grocery Sales & Operations Power BI Dashboard**.

---

## 3 Ways to Access & Present the Dashboard

### Option 1: Live Interactive Browser Dashboard (Zero Setup)
Open the standalone interactive Power BI replica in your web browser:
[`grocery_power_bi_dashboard.html`](file:///C:/Users/Krisha%20Jariwala/.gemini/antigravity/scratch/data_analyst_portfolio/03_grocery_sales_data_analysis/power_bi/grocery_power_bi_dashboard.html)
- Fully interactive slicers (Department, Organic Status, Store Location).
- Real-time FMCG retail KPI calculation updates.
- 3 report pages: Assortment & Product Velocity, Organic vs Conventional Margin, Store Operations & Pareto 80/20.
- Ideal for portfolio websites, GitHub Pages, or sharing with recruiters who don't have Power BI Desktop installed!

### Option 2: Native Power BI Desktop Project (`.pbip`)
If you have **Power BI Desktop** installed:
1. Double-click [`Grocery_Sales_Dashboard.pbip`](file:///C:/Users/Krisha%20Jariwala/.gemini/antigravity/scratch/data_analyst_portfolio/03_grocery_sales_data_analysis/power_bi/Grocery_Sales_Dashboard.pbip).
2. Power BI Desktop opens automatically with:
   - Clean tabular dataset (`Cleaned_Grocery_Sales`).
   - Pre-loaded DAX retail measures ([`DAX_KPIS.md`](file:///C:/Users/Krisha%20Jariwala/.gemini/antigravity/scratch/data_analyst_portfolio/03_grocery_sales_data_analysis/power_bi/DAX_KPIS.md)).
   - Data source connections pointing directly to your local CSVs.

### Option 3: Build from Scratch in Power BI Desktop (Standard PBIX)
Follow the step-by-step layout specifications below.

---

## Visual Layout & Canvas Specifications (16:9 - 1280 x 720 px)

### Theme & Color Palette
- **Primary Accent:** `#059669` (Fresh Emerald Green)
- **Secondary Dark:** `#064E3B` (Deep Forest)
- **Soft Light Accent:** `#D1FAE5` (Mint Foam)
- **Department Callouts:** `#10B981` (Produce), `#EF4444` (Meat & Seafood), `#3B82F6` (Dairy & Eggs), `#F59E0B` (Bakery), `#8B5CF6` (Beverages)

---

### Page 1: Assortment & Product Velocity

#### 1. KPI Card Ribbon (Top, Y: 10px, Height: 90px)
| Card Title | Measure Expression | Formatting | Callout Value Display |
| :--- | :--- | :--- | :--- |
| **Total Revenue** | `[Total Grocery Revenue]` | Currency (`$#,##0.00`) | $38,420 (Green font) |
| **Gross Profit** | `[Gross Profit]` | Currency (`$#,##0.00`) | $20,250 |
| **Gross Margin %**| `[Gross Margin %]` | Percentage (`0.0%`) | 52.7% |
| **Avg Basket Size**| `[Average Basket Size]` | Decimal (`0.00`) | 2.15 Units |
| **Avg Basket Value**| `[Average Basket Value]`| Currency (`$#,##0.00`) | $12.80 |
| **Top Anchor SKU** | String Callout | Text | Organic Bananas (14.2 / day) |

#### 2. Department Revenue Contribution (Horizontal Bar Chart)
- **X-Axis:** `[Total Grocery Revenue]`
- **Y-Axis:** `Cleaned_Grocery_Sales[Category]`
- **Data Labels:** Turn On, Position: Outside End.
- **Color Coding:** Highlight Produce (`#10B981`) and Meat & Seafood (`#EF4444`) which drive 60% of total supermarket turnover.

#### 3. Organic Revenue Penetration (Donut Chart)
- **Legend:** `Cleaned_Grocery_Sales[Is_Organic]` (1 = Organic, 0 = Conventional)
- **Values:** `[Total Grocery Revenue]`
- **Details:** Organic (28.4% share, $10,910), Conventional (71.6% share, $27,510).

#### 4. Top 10 SKU Velocity Leaderboard (Table Visual)
- **Columns:** `Standard_Product_Name`, `Category`, `Is_Organic`, `Unit_Price`, `Quantity_Sold`, `[Product Velocity]`, `[Gross Margin %]`
- **Conditional Formatting:** Add Data Bars to `[Product Velocity]` and green-to-red color gradient to `[Gross Margin %]`.

---

### Page 2: Organic vs Conventional Profitability

#### 1. Margin % Clustered Bar Visual
- **X-Axis:** `Cleaned_Grocery_Sales[Is_Organic]`
- **Y-Axis:** `[Gross Margin %]`
- **Callout:** Add a text box or KPI card displaying `[Organic Margin Premium %]` = **+8.4%**.

#### 2. Store Location Assortment Penetration (Matrix Visual)
- **Rows:** `Cleaned_Grocery_Sales[Store_Location]`
- **Values:** `[Total Grocery Revenue]`, `[Organic Revenue Share %]`, `[Gross Margin %]`
- **Insight:** Surfaces `STORE-WEST-02` leading organic sales at 34.1% penetration.

---

### Page 3: Store Operations & Pareto 80/20 Curve

#### 1. Pareto 80/20 Assortment Curve (Line & Clustered Column Chart)
- **Shared X-Axis:** `Cleaned_Grocery_Sales[Standard_Product_Name]` (Sorted descending by revenue)
- **Column Values:** `[Total Grocery Revenue]`
- **Line Values:** `[Pareto Cumulative Revenue %]`
- **Reference Line:** Constant line at **80%** on the Secondary Y-Axis.
- **Insight:** Demonstrates that the top 4 SKUs (Bananas, Salmon, Chicken, Milk) account for 80.2% of store cash flow.
