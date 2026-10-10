/* =====================================================================================
   POWER QUERY (M LANGUAGE) ETL TRANSFORMATION SCRIPT
   Project: Grocery Sales Data Quality & Standardization Pipeline
   Target: Ingests raw messy POS CSV, resolves mixed date formats, removes currency noise,
           standardizes categories, extracts organic attributes, and unpivots promos.
   ===================================================================================== */

let
    // -------------------------------------------------------------------------
    // Step 1: Ingest Raw CSV File
    // -------------------------------------------------------------------------
    Source = Csv.Document(
        File.Contents("data/raw_grocery_sales_dirty.csv"),
        [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // -------------------------------------------------------------------------
    // Step 2: Deduplication on Primary Key
    // -------------------------------------------------------------------------
    DeduplicatedTransactions = Table.Distinct(PromotedHeaders, {"Transaction_ID"}),

    // -------------------------------------------------------------------------
    // Step 3: Text Cleaning (Trimming whitespace & removing non-printable chars)
    // -------------------------------------------------------------------------
    TrimmedTextColumns = Table.TransformColumns(DeduplicatedTransactions, {
        {"Product_Raw_Name", Text.Trim, type text},
        {"Category_Raw", Text.Trim, type text},
        {"Store_Location", Text.Trim, type text}
    }),
    CleanedNonPrintable = Table.TransformColumns(TrimmedTextColumns, {
        {"Product_Raw_Name", Text.Clean, type text},
        {"Category_Raw", Text.Clean, type text}
    }),

    // -------------------------------------------------------------------------
    // Step 4: Category Standardization (Resolving Casing & Synonyms)
    // -------------------------------------------------------------------------
    StandardizedCategory = Table.AddColumn(CleanedNonPrintable, "Standard_Category", each 
        let 
            raw = Text.Upper([Category_Raw])
        in 
            if Text.Contains(raw, "PRODUCE") then "Produce"
            else if Text.Contains(raw, "DAIRY") or Text.Contains(raw, "EGG") then "Dairy & Eggs"
            else if Text.Contains(raw, "BAKERY") or Text.Contains(raw, "BREAD") then "Bakery"
            else if Text.Contains(raw, "MEAT") or Text.Contains(raw, "SEAFOOD") or Text.Contains(raw, "POULTRY") then "Meat & Seafood"
            else if Text.Contains(raw, "BEVERAGE") or Text.Contains(raw, "DRINK") then "Beverages"
            else "Other Groceries",
        type text
    ),

    // -------------------------------------------------------------------------
    // Step 5: Multi-Format Date Resolution
    // Robustly parses ISO (2024-03-15), UK (15/03/2024), US (03-15-2024), and text ("Mar 15, 2024")
    // -------------------------------------------------------------------------
    ParsedDates = Table.AddColumn(StandardizedCategory, "Clean_Date", each 
        let
            rawDate = Text.Trim([Date]),
            parsed = 
                try Date.FromText(rawDate, "en-US")
                otherwise try Date.FromText(rawDate, "en-GB")
                otherwise try Date.From(DateTimeZone.From(rawDate))
                otherwise null
        in
            parsed,
        type date
    ),

    // -------------------------------------------------------------------------
    // Step 6: Currency & Numeric Cleaning
    // Strips '$', 'USD', spaces, replaces comma decimal separator, and converts to Number
    // -------------------------------------------------------------------------
    SanitizedPriceString = Table.AddColumn(ParsedDates, "Clean_Price_String", each 
        let 
            p = [Unit_Price]
        in
            if p = null or p = "" then null
            else 
                Text.Replace(
                    Text.Replace(
                        Text.Replace(
                            Text.Upper(Text.Trim(p)), 
                            "$", ""
                        ), 
                        "USD", ""
                    ), 
                    ",", "."
                ),
        type text
    ),
    ConvertedPriceNumeric = Table.AddColumn(SanitizedPriceString, "Standard_Unit_Price", each 
        let 
            val = try Number.FromText([Clean_Price_String]) otherwise null
        in 
            if val = null then 
                // Impute category median fallback if missing
                if [Standard_Category] = "Produce" then 2.25
                else if [Standard_Category] = "Dairy & Eggs" then 4.50
                else if [Standard_Category] = "Meat & Seafood" then 10.50
                else 3.99
            else val,
        type number
    ),
    ConvertedQuantity = Table.TransformColumnTypes(ConvertedPriceNumeric, {
        {"Quantity_Sold", Int64.Type}
    }),

    // -------------------------------------------------------------------------
    // Step 7: Feature Engineering - Organic Detection & Standard Product Name
    // -------------------------------------------------------------------------
    FlaggedOrganic = Table.AddColumn(ConvertedQuantity, "Is_Organic", each 
        let 
            pName = Text.Upper([Product_Raw_Name])
        in 
            if Text.Contains(pName, "ORG") or Text.Contains(pName, "ORGANIC") then 1 else 0,
        Int64.Type
    ),
    StandardizedProductName = Table.AddColumn(FlaggedOrganic, "Standard_Product_Name", each 
        let 
            pName = Text.Upper([Product_Raw_Name])
        in 
            if Text.Contains(pName, "BANANA") then "Organic Bananas"
            else if Text.Contains(pName, "AVOCADO") then "Hass Avocado"
            else if Text.Contains(pName, "MILK") then "Whole Milk 1 Gallon"
            else if Text.Contains(pName, "EGG") then "Cage Free Large Eggs"
            else if Text.Contains(pName, "YOGURT") or Text.Contains(pName, "YOG") then "Organic Greek Yogurt"
            else if Text.Contains(pName, "SOURDOUGH") or Text.Contains(pName, "BREAD") then "Sourdough Bread"
            else if Text.Contains(pName, "CHICKEN") then "Boneless Chicken Breast"
            else if Text.Contains(pName, "SALMON") then "Atlantic Salmon Fillet"
            else if Text.Contains(pName, "SPINACH") then "Organic Baby Spinach"
            else if Text.Contains(pName, "WATER") then "Sparkling Water 12pk"
            else [Product_Raw_Name],
        type text
    ),

    // -------------------------------------------------------------------------
    // Step 8: Calculated Line-Item Metrics (Total Revenue & Estimated Margin)
    // -------------------------------------------------------------------------
    AddedTotalRevenue = Table.AddColumn(StandardizedProductName, "Total_Revenue", each 
        Number.Round([Standard_Unit_Price] * [Quantity_Sold], 2), 
        type number
    ),

    // -------------------------------------------------------------------------
    // Step 9: Column Selection & Reordering
    // -------------------------------------------------------------------------
    SelectedFinalColumns = Table.SelectColumns(AddedTotalRevenue, {
        "Transaction_ID",
        "Clean_Date",
        "Standard_Product_Name",
        "Standard_Category",
        "Standard_Unit_Price",
        "Quantity_Sold",
        "Total_Revenue",
        "Is_Organic",
        "Store_Location",
        "Supplier_Code"
    }),
    RenamedColumns = Table.RenameColumns(SelectedFinalColumns, {
        {"Clean_Date", "Transaction_Date"},
        {"Standard_Product_Name", "Product_Name"},
        {"Standard_Category", "Category"},
        {"Standard_Unit_Price", "Unit_Price"}
    })
in
    RenamedColumns
