import frappe
from frappe.utils import flt
@frappe.whitelist()
def finish_stock_entry(job_card_name):
    """Create a Material Request (Material Transfer) from Job Card Dyeing child tables"""

    # Load the Job Card Dyeing document
    job_card = frappe.get_doc("Job Card Production", job_card_name)

    # check existing mr
    existing_se = frappe.db.get_value(
    "Stock Entry",
    {
        "custom_job_card_production_finish": job_card.name,
        "docstatus": ("!=", 2),
        "stock_entry_type": "Manufacture"  
    },
    ["name"],
    as_dict=True
    )

    if existing_se:
        frappe.throw(
                f"Stock Entry {existing_se.name} already exists with type {existing_se.stock_entry_type}. "
            )
    # Create new Material Request doc
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Manufacture"
    se.set_posting_time = 1
    se.company = job_card.company if hasattr(job_card, "company") else frappe.defaults.get_global_default("company")
    se.posting_date = job_card.date or frappe.utils.today()
    se.posting_time = frappe.utils.nowtime()
    se.custom_job_card_production_finish = job_card.name

    # --- Pull items from raw_item_chamicals child table ---
    if not job_card.finish_item:
        frappe.throw("Finish Item is required")
    item = frappe.get_doc("Item", job_card.finish_item)
    se.append("items", {
        "item_code": job_card.finish_item,
        "stock_uom": item.stock_uom,
        "uom": item.stock_uom,
        "qty": job_card.qty,
        "t_warehouse": job_card.finish_warehouse,
        "is_finished_item": 1
        
    })

    if item.has_batch_no:   
        se["items"][0].update({
            "batch_no": job_card.batch
        })
    
    for item in job_card.raw_item_chamicals:
        se.append("items", {
            "item_code": item.item,
            "stock_uom": item.uom,
            "uom": item.uom,
            "qty": item.qty_required,
            "s_warehouse": job_card.production_warehouse
           
        })

    # Insert into DB
    se.insert(ignore_permissions=True)

    # Optional: submit if required
    se.submit()

    return se.name


 
        
