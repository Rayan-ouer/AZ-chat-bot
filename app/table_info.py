table_info = {
    "items": {
        "description": "Products and commercial data",
        "columns": {
            "id": "Product ID",
            "code": "Product code",
            "name": "Name",
            "cost_price": "Cost",
            "sale_price": "Price",
            "stock_min": "Min stock",
            "stock_max": "Max stock",
            "location": "Location",
            "is_active": "Active (1/0)",
        },
    },
    "stocks": {
        "description": "Stock levels per store",
        "columns": {
            "item_id": "Product ID",
            "store_id": "Store ID",
            "quantity": "Stock qty",
            "min_quantity": "Min threshold",
            "max_quantity": "Max threshold",
        },
    },
    "stock_movements": {
        "description": "Inbound/outbound stock history",
        "columns": {
            "item_id": "Product ID",
            "store_id": "Store ID",
            "quantity": "Qty (+in/-out)",
            "cost_price": "Unit cost",
            "type": "Type (achat, vente...)",
            "reference": "Doc ref",
            "note": "Note",
            "created_at": "Date",
        },
    },
    "delivery_note_lines": {
        "description": "Delivered items per note",
        "columns": {
            "article_code": "Item code",
            "delivered_quantity": "Qty",
            "unit_price_ht": "Price HT",
            "unit_price_ttc": "Price TTC",
            "remise": "Discount %",
            "total_ligne_ht": "Total HT",
            "total_ligne_ttc": "Total TTC",
        },
    },
    "invoice_lines": {
        "description": "Invoice item details",
        "columns": {
            "article_code": "Item code",
            "quantity": "Qty",
            "unit_price_ht": "Price HT",
            "remise": "Discount %",
            "total_ligne_ht": "Total HT",
            "total_ligne_ttc": "Total TTC",
        },
    },
    "invoices": {
        "description": "Issued invoices",
        "columns": {
            "numdoc": "Doc number",
            "invoice_date": "Date",
            "status": "Status",
            "paid": "Paid (1/0)",
            "total_ht": "Total HT",
            "total_ttc": "Total TTC",
            "tva_rate": "VAT %",
        },
    },
    "sales_return_lines": {
        "description": "Returned items",
        "columns": {
            "article_code": "Item code",
            "returned_quantity": "Qty",
            "unit_price_ht": "Price HT",
            "remise": "Discount %",
            "total_ligne_ht": "Total HT",
        },
    },
    "sales_returns": {
        "description": "Sales return docs",
        "columns": {
            "numdoc": "Doc number",
            "return_date": "Date",
            "type": "Type (total/partial)",
            "total_ht": "Total HT",
            "total_ttc": "Total TTC",
            "tva_rate": "VAT %",
            "invoiced": "Invoiced (1/0)",
        },
    },
    "item_categories": {
        "description": "Product categories",
        "columns": {
            "name": "Category name",
        },
    },
    "item_equivalents": {
        "description": "Equivalent items",
        "columns": {
            "reason": "Reason",
        },
    },
    "suppliers": {
        "description": "Supplier info",
        "columns": {
            "id": "Supplier ID",
            "code": "Code",
            "name": "Name",
            "solde": "Balance",
            "plafond": "Credit limit",
            "risque": "Risk level",
            "blocked": "Blocked (1/0)",
        },
    },
    "vehicles": {
        "description": "Vehicle data",
        "columns": {
            "id": "Vehicle ID",
            "brand_name": "Brand",
            "model_name": "Model",
            "engine_description": "Engine",
            "license_plate": "Plate",
        },
    },
}
