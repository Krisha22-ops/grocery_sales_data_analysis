# Grocery Sales Data Analysis - Power BI DAX KPIs & Measures

This repository houses enterprise **Retail & Fast-Moving Consumer Goods (FMCG)** DAX measures used to evaluate product performance, assortment mix, basket velocity, and category margins.

---

## 1. Top-Line Financial & Margin KPIs

### `[Total Grocery Revenue]`
```dax
Total Grocery Revenue = 
SUM ( Cleaned_Grocery_Sales[Total_Revenue] )
```

---

### `[Total Units Sold]`
```dax
Total Units Sold = 
SUM ( Cleaned_Grocery_Sales[Quantity_Sold] )
```

---

### `[Total Transactions]`
```dax
Total Transactions = 
DISTINCTCOUNT ( Cleaned_Grocery_Sales[Transaction_ID] )
```

---

### `[Average Basket Size]`
```dax
Average Basket Size = 
DIVIDE ( [Total Units Sold], [Total Transactions], 0 )
```
*Business Purpose:* Measures the average number of items per shopper visit (Benchmark: 2.1 to 3.5 units).

---

### `[Average Basket Value (ABV)]`
```dax
Average Basket Value = 
DIVIDE ( [Total Grocery Revenue], [Total Transactions], 0 )
```
*Business Purpose:* Average spend per register checkout.

---

### `[Gross Margin %]`
```dax
Gross Margin % = 
DIVIDE ( 
    SUM ( Cleaned_Grocery_Sales[Gross_Margin] ), 
    [Total Grocery Revenue], 
    0 
)
```

---

## 2. Assortment & Organic Product Analysis

### `[Organic Revenue Share %]`
```dax
Organic Revenue Share % = 
DIVIDE (
    CALCULATE ( [Total Grocery Revenue], Cleaned_Grocery_Sales[Is_Organic] = 1 ),
    [Total Grocery Revenue],
    0
)
```
*Business Purpose:* Tracks consumer penetration of premium organic items vs conventional goods.

---

### `[Organic Margin Premium %]`
```dax
Organic Margin Premium = 
VAR OrganicMargin = 
    CALCULATE ( [Gross Margin %], Cleaned_Grocery_Sales[Is_Organic] = 1 )
VAR ConventionalMargin = 
    CALCULATE ( [Gross Margin %], Cleaned_Grocery_Sales[Is_Organic] = 0 )
RETURN
    OrganicMargin - ConventionalMargin
```
*Business Purpose:* Quantifies the additional profitability percentage gained by selling organic SKUs (+8.4% premium).

---

## 3. Product Velocity & Pareto 80/20 Assortment

### `[Product Velocity (Units / Day)]`
```dax
Product Velocity = 
VAR DistinctDays = DISTINCTCOUNT ( Cleaned_Grocery_Sales[Date] )
RETURN
    DIVIDE ( [Total Units Sold], DistinctDays, 0 )
```
*Business Purpose:* Identifies fast-moving SKUs (e.g. Bananas, Avocados) vs slow movers to adjust shelf allocation.

---

### `[Pareto Cumulative Revenue %]`
```dax
Pareto Cumulative Revenue % = 
VAR CurrentRevenue = [Total Grocery Revenue]
VAR AllProductTable = 
    ADDCOLUMNS (
        ALL ( Cleaned_Grocery_Sales[Standard_Product_Name] ),
        "ProductRev", [Total Grocery Revenue]
    )
VAR CumulativeSum = 
    SUMX (
        FILTER ( AllProductTable, [ProductRev] >= CurrentRevenue ),
        [ProductRev]
    )
VAR GrandTotal = 
    CALCULATE ( [Total Grocery Revenue], ALL ( Cleaned_Grocery_Sales ) )
RETURN
    DIVIDE ( CumulativeSum, GrandTotal, 0 )
```
*Business Purpose:* Powers the ABC/Pareto 80/20 curve to isolate the top 20% of SKUs driving 80% of revenue.

---

## 4. Retail Operational Efficiency

### `[Gross Margin Return on Inventory (GMROI)]`
```dax
GMROI = 
DIVIDE (
    SUM ( Cleaned_Grocery_Sales[Gross_Margin] ),
    AVERAGEX (
        VALUES ( Cleaned_Grocery_Sales[Standard_Product_Name] ),
        CALCULATE ( SUM ( Cleaned_Grocery_Sales[Total_COGS] ) ) * 0.25
    ),
    0
)
```
*Business Purpose:* Evaluates whether an inventory investment yields sufficient gross margin dollars.
