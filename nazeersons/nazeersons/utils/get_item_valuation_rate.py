import frappe

@frappe.whitelist()
def get_item_valuation_rate(item_code, warehouse=None):
    """
    Returns the valuation rate of an item.
    If warehouse is provided, limits to that warehouse; otherwise uses latest Stock Ledger Entry overall.
    """

    if not item_code:
        frappe.throw("Item Code is required")

    sle_filters = {
        "item_code": item_code,
        "is_cancelled": 0
    }
    if warehouse:
        sle_filters["warehouse"] = warehouse

    sle = frappe.get_list(
        "Stock Ledger Entry",
        filters = sle_filters,
        fields = ["valuation_rate"],
        order_by = "posting_date DESC, posting_time DESC",
        limit = 1
    )

    if sle and len(sle) > 0:
        return sle[0].valuation_rate
    else:
        return 0.0
