"""
Dirty Raw Grocery Sales Data Generator
======================================
Simulates enterprise data ingestion challenges:
1. Inconsistent naming and casing ('org bananas', 'BANANAS Organic', 'Banana - Org. 1lb').
2. Multi-format date strings ('2024-03-12', '12/03/2024', 'Mar 12, 2024').
3. Dirty numeric values ('$4.99', '4.99 USD', '4,99', nulls).
4. Category misspellings and casing ('Produce', 'PRODUCE', 'Fresh Produce', 'dairy & eggs').
5. Duplicate transactions and mixed promotions.
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

random.seed(101)
np.random.seed(101)

def generate_grocery_data(base_dir: str):
    data_dir = Path(base_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    products_master = [
        # (Clean Product, Clean Category, Price, Cost, Organic, Variations)
        ("Organic Bananas", "Produce", 1.99, 0.85, 1, 
         ["  org bananas 1lb ", "BANANAS Organic", "Banana - Org. 1lb", "organic bananas (1 lb)", "Bananas Org"]),
        ("Hass Avocado", "Produce", 2.49, 1.10, 0, 
         ["HASS AVOCADO 4ct", "Avocado - Hass (4 Pack)  ", "hass avocado 4 pack", "AVOCADO HASS", "Avocado Hass 4ct"]),
        ("Whole Milk 1 Gallon", "Dairy & Eggs", 3.89, 2.10, 0, 
         ["whole milk 1 gal", "Milk Whole 1GAL", "  WHOLE MILK 1 GALLON", "Whole Milk - 1 Gal", "Milk, Whole 1 Gal"]),
        ("Cage Free Large Eggs", "Dairy & Eggs", 4.29, 2.30, 0, 
         ["Eggs Cage Free 12ct", "CAGE FREE EGGS (DOZEN)", "eggs - cage-free lg 12", "Cage Free Large Eggs 12pk"]),
        ("Organic Greek Yogurt", "Dairy & Eggs", 5.49, 2.80, 1, 
         ["Org Greek Yogurt 32oz", "YOGURT GREEK ORGANIC", "organic plain greek yogurt", "Org Greek Yog 32 oz"]),
        ("Sourdough Bread", "Bakery", 4.79, 1.90, 0, 
         ["sourdough bread loaf", "BREAD SOURDOUGH ARTISAN", "Sourdough Bread 16oz  ", "Sourdough Loaf"]),
        ("Boneless Chicken Breast", "Meat & Seafood", 8.99, 5.20, 0, 
         ["CHICKEN BREAST BNLS 1LB", "boneless chicken breast", "Chicken Breast - Boneless/Skinless", "Chicken Breast B/S"]),
        ("Atlantic Salmon Fillet", "Meat & Seafood", 12.99, 7.80, 0, 
         ["salmon fillet fresh 1lb", "ATLANTIC SALMON FILLET", "Fresh Salmon Fillet", "Salmon - Atlantic 1 lb"]),
        ("Organic Baby Spinach", "Produce", 3.49, 1.40, 1, 
         ["baby spinach organic 5oz", "ORGANIC BABY SPINACH 5 OZ", "Org Spinach Baby 5oz", "Baby Spinach - Org"]),
        ("Sparkling Water 12pk", "Beverages", 5.99, 3.10, 0, 
         ["sparkling water lime 12pk", "SPARKLING WATER 12 PACK", "Sparkling Water - Lime 12ct", "Spk Water 12pk"])
    ]

    category_variations = {
        "Produce": ["Produce", "PRODUCE", "Fresh Produce", "produce "],
        "Dairy & Eggs": ["Dairy & Eggs", "DAIRY", "dairy & eggs", "Dairy", "Dairy/Eggs"],
        "Bakery": ["Bakery", "BAKERY", "bakery & bread", "Bakery Fresh"],
        "Meat & Seafood": ["Meat & Seafood", "MEAT", "meat & poultry", "Meat/Seafood"],
        "Beverages": ["Beverages", "BEVERAGES", "beverages", "Drinks & Beverages"]
    }

    date_formats = [
        lambda d: d.strftime("%Y-%m-%d"),
        lambda d: d.strftime("%d/%m/%Y"),
        lambda d: d.strftime("%m-%d-%Y"),
        lambda d: d.strftime("%b %d, %Y")
    ]

    n_rows = 3000
    start_date = datetime(2024, 1, 1)
    
    raw_rows = []
    clean_rows = []
    
    for i in range(n_rows):
        prod = random.choice(products_master)
        clean_name, clean_cat, clean_price, clean_cost, is_org, dirty_names = prod
        
        # Pick random dirty variations
        dirty_name = random.choice(dirty_names)
        dirty_cat = random.choice(category_variations[clean_cat])
        
        # Random date within 2024
        d = start_date + timedelta(days=random.randint(0, 300))
        date_formatter = random.choice(date_formats)
        dirty_date = date_formatter(d)
        clean_date = d.strftime("%Y-%m-%d")
        
        # Quantity
        qty = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.30, 0.15, 0.07, 0.03])[0]
        
        # Dirty price formatting
        price_noise_type = random.choice(["standard", "currency_prefix", "usd_suffix", "comma", "null"])
        if price_noise_type == "currency_prefix":
            dirty_price = f"${clean_price:.2f}"
        elif price_noise_type == "usd_suffix":
            dirty_price = f"{clean_price:.2f} USD"
        elif price_noise_type == "comma":
            dirty_price = f"{str(clean_price).replace('.', ',')}"
        elif price_noise_type == "null" and random.random() < 0.05:
            dirty_price = None
        else:
            dirty_price = str(clean_price)
            
        txn_id = f"GROC-{10000 + i}"
        store_id = random.choice(["STORE-EAST-01", "STORE-WEST-02", "STORE-CENTRAL-03", "STORE-NORTH-04"])
        
        raw_rows.append({
            "Transaction_ID": txn_id,
            "Date": dirty_date,
            "Product_Raw_Name": dirty_name,
            "Category_Raw": dirty_cat,
            "Unit_Price": dirty_price,
            "Quantity_Sold": qty,
            "Store_Location": store_id,
            "Supplier_Code": f"SUPP-{random.randint(10, 25)}",
            "Q1_Promo": "Yes" if random.random() < 0.25 else "No",
            "Q2_Promo": "Yes" if random.random() < 0.20 else "No"
        })
        
        # Build clean counterpart
        total_rev = round(clean_price * qty, 2)
        total_cogs = round(clean_cost * qty, 2)
        margin = round(total_rev - total_cogs, 2)
        margin_pct = round((margin / total_rev) * 100, 1)
        
        clean_rows.append({
            "Transaction_ID": txn_id,
            "Date": clean_date,
            "Standard_Product_Name": clean_name,
            "Category": clean_cat,
            "Unit_Price": clean_price,
            "Unit_Cost": clean_cost,
            "Quantity_Sold": qty,
            "Total_Revenue": total_rev,
            "Total_COGS": total_cogs,
            "Gross_Margin": margin,
            "Gross_Margin_Pct": margin_pct,
            "Is_Organic": is_org,
            "Store_Location": store_id
        })

    # Inject duplicate transaction IDs with noise to simulate dirty ERP dumps
    for _ in range(50):
        dup_idx = random.randint(0, len(raw_rows) - 1)
        raw_rows.append(raw_rows[dup_idx].copy())

    raw_df = pd.DataFrame(raw_rows)
    clean_df = pd.DataFrame(clean_rows)

    raw_csv = data_dir / "raw_grocery_sales_dirty.csv"
    clean_csv = data_dir / "cleaned_grocery_sales.csv"

    raw_df.to_csv(raw_csv, index=False)
    clean_df.to_csv(clean_csv, index=False)

    print(f"Generated {len(raw_df)} dirty grocery records at {raw_csv}")
    print(f"Generated {len(clean_df)} cleaned benchmark records at {clean_csv}")

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    generate_grocery_data(str(current_dir))
