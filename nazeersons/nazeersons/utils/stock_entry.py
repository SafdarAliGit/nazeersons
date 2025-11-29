# your_app/hooks_stock_entry_update.py
import frappe

def custom_on_update_stock_entry(doc, method):
    # Only proceed if master fields are present
    customer = doc.get("customer")
    challan_no = doc.get("customer_challan_no")
    if not (customer and challan_no):
        return

    for item in doc.get("items") or []:
        batch_no = item.get("batch_no")
        if not batch_no:
            continue

        try:
            batch_doc = frappe.get_doc("Batch", batch_no)
        except frappe.DoesNotExistError:
            continue

        batch_doc.customer = customer
        batch_doc.customer_challan_no = challan_no
        batch_doc.save()
    
    # Optional: push updates
    frappe.db.commit()
