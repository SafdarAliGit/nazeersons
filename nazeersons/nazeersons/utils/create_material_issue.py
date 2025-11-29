import frappe
from frappe.utils import flt


@frappe.whitelist()
def create_material_issue(docname):
    """Create Stock Entry (Material Transfer) from greige_fabric_detail child table"""
    parent_doc = frappe.get_doc("Job Card Dyeing", docname)

    if not parent_doc.greige_fabric_detail:
        frappe.throw("No Fabric Details found to create Stock Entry.")

    # 🔎 Check if a Stock Entry already exists (not cancelled, not Material Transfer)
    existing_se = frappe.db.get_value(
        "Stock Entry",
        {
            "custom_job_card_production": parent_doc.name,
            "docstatus": ("!=", 2),
            "stock_entry_type": "Material Transfer"  
        },
        ["name"],
        as_dict=True
    )

    if existing_se:
        frappe.throw(
                f"Stock Entry {existing_se.name} already exists with type {existing_se.stock_entry_type}. "
            )

    # 🚀 Create new Stock Entry
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Transfer"
    se.posting_date = parent_doc.date or frappe.utils.today()
    se.posting_time = frappe.utils.nowtime()
    se.custom_job_card_dyeing = parent_doc.name  # custom link field

    for row in parent_doc.greige_fabric_detail:
        if not row.fabric_item:
            continue

        item = frappe.get_doc("Item", row.fabric_item)
        se.append("items", {
            "item_code": row.fabric_item,
            "qty": flt(row.qty_issue),
            "uom": item.stock_uom,
            "s_warehouse": parent_doc.greige_fabric_store,
            "t_warehouse": parent_doc.production_warehouse,
            "batch_no": row.lot,
            "allow_zero_valuation_rate": 1,
            "use_serial_batch_fields": 1
        })

    se.insert(ignore_permissions=True)
    se.submit()


