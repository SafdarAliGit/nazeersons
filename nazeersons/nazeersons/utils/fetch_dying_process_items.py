import frappe

@frappe.whitelist()
def fetch_dying_process_items(**args):
    ref_shade_no = args.get('ref_shade_no')
    dpi_query = frappe.get_all(
        "Dyeing Process Item",
        filters={"parent": ref_shade_no},
        fields=["dyeing_process", "overhead_account", "amount"]
    )

    return {
        'dyeing_process_items': dpi_query,
    }

