import frappe

@frappe.whitelist()
def fetch_sub_operations(operation):
    if not operation:
        frappe.throw(_("Operation name is required"))

    operations = frappe.get_all(
    "Sub Operation",
    filters={"parent": operation},
    fields=["operation"]
    )

    return {"operations": operations}
