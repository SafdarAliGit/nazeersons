# your_app/api.py
import frappe

@frappe.whitelist()
def fetch_recipe(finish_item, warehouse=None):
    """
    Fetch recipe lines and attach valuation_rate and qty_after_transaction (from Stock Ledger Entry) per item.
    """

    if not finish_item:
        return {"recipe": []}

    # ✅ 1. Get recipe lines
    recipe = frappe.get_all(
        "Item Recipe",
        filters={"parent": finish_item},
        fields=["item", "qty", "uom", "rate", "amount"],
        order_by="idx"
    )

    if not recipe:
        return {"recipe": []}

    # ✅ 2. Get distinct items
    items = list({row.get("item") for row in recipe if row.get("item")})

    # ✅ 3. Prepare valuation mapping per item
    val_map = {}
    for item_code in items:
        if not item_code:
            continue

        sle_filters = {
            "item_code": item_code,
            "is_cancelled": 0
        }
        if warehouse:
            sle_filters["warehouse"] = warehouse

        sle = frappe.get_list(
            "Stock Ledger Entry",
            filters=sle_filters,
            fields=["valuation_rate", "qty_after_transaction"],
            order_by="posting_date DESC, posting_time DESC",
            limit=1
        )

        if sle:
            valuation_rate = sle[0].valuation_rate or 0.0
            qty_after_transaction = sle[0].qty_after_transaction or 0.0
        else:
            valuation_rate = 0.0
            qty_after_transaction = 0.0

        val_map[item_code] = {
            "valuation_rate": valuation_rate,
            "qty_after_transaction": qty_after_transaction
        }

    # ✅ 4. Build final recipe list
    recipe_with_valuation = []
    for row in recipe:
        item_code = row.get("item")
        val_info = val_map.get(item_code, {"valuation_rate": 0.0, "qty_after_transaction": 0.0})

        new_row = row.copy()
        new_row["valuation_rate"] = val_info["valuation_rate"]
        new_row["qty_after_transaction"] = val_info["qty_after_transaction"]
        recipe_with_valuation.append(new_row)

    return {
        "recipe": recipe_with_valuation
    }
