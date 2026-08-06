import frappe
from frappe.utils import flt


def clamp_consolidated_return_rates(doc, method=None):
    if not (doc.get("is_consolidated") and doc.get("is_return")):
        return
    if doc.docstatus > 0 or not doc.get("return_against"):
        return

    for item in doc.items:
        if not item.get("sales_invoice_item"):
            continue

        ref_rate = frappe.db.get_value(
            "Sales Invoice Item", item.sales_invoice_item, "rate"
        )
        if ref_rate is None or flt(item.rate) <= flt(ref_rate):
            continue

        item.rate = flt(ref_rate)
        item.price_list_rate = flt(ref_rate)
        item.discount_percentage = 0
        item.discount_amount = 0
        item.margin_rate_or_amount = 0
        item.rate_with_margin = 0
        item.amount = flt(item.rate) * flt(item.qty)