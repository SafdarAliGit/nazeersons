import json

import frappe

@frappe.whitelist()
def from_shade_process(**args):
    names = args.get('names', None)
    dpi_query = frappe.get_all(
        "Shade Process",
        filters={"docstatus": 1, "name": ["in", json.loads(names)]},
        fields=["name", "total_cost","fabric_type","service_item","finish_item","color"]
    )

    return {'shade_process': dpi_query}
