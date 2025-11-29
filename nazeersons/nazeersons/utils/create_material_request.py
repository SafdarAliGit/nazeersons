import frappe
from frappe.utils import flt
@frappe.whitelist()
def create_material_request_chemicals_and_dyes(job_card_name):
    """Create a Material Request (Material Transfer) from Job Card Dyeing child tables"""

    # Load the Job Card Dyeing document
    job_card = frappe.get_doc("Job Card Production", job_card_name)

    # check existing mr
    existing_mr = frappe.db.get_value(
    "Material Request",
    {
        "custom_job_card_production": job_card.name,
        "docstatus": ("!=", 2),
        "material_request_type": "Material Transfer"  
    },
    ["name"],
    as_dict=True
    )

    if existing_mr:
        frappe.throw(
                f"Material Request {existing_mr.name} already exists with type {existing_mr.material_request_type}. "
            )
    # Create new Material Request doc
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Material Transfer"
    mr.company = job_card.company if hasattr(job_card, "company") else frappe.defaults.get_global_default("company")
    mr.transaction_date = job_card.date or frappe.utils.today()
    mr.custom_job_card_production = job_card.name

    # --- Pull items from raw_item_chamicals child table ---
    for item in job_card.raw_item_chamicals:
        mr.append("items", {
            "item_code": item.item,
            "stock_uom": item.uom,
            "uom": item.uom,
            "qty": item.qty_required,
            "from_warehouse": job_card.chemicals_store,
            "warehouse": job_card.production_warehouse,
            "schedule_date": job_card.date
        })

    # Insert into DB
    mr.insert(ignore_permissions=True)

    # Optional: submit if required
    mr.submit()

    return mr.name
