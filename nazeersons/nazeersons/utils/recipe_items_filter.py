import frappe

@frappe.whitelist()
def recipe_items_filter(doctype, txt, searchfield, start, page_len, filters):
    """
    Custom link query:
    - Fetch Items in Item Group "Raw Material"
    - Include all sub-groups under it
    """

    # 1️⃣ Get nested set left/right bounds for "Raw Material"
    group_bounds = frappe.db.get_value(
        "Item Group",
        "Raw Material",
        ["lft", "rgt"],
        as_dict=True,
    )

    if not group_bounds:
        return []

    # 2️⃣ Query items under Raw Material and *all its child groups*
    return frappe.db.sql(
        """
        SELECT
            i.name,
            i.item_name
        FROM
            `tabItem` i
        JOIN
            `tabItem Group` ig
            ON ig.name = i.item_group
        WHERE
            ig.lft >= %(lft)s
            AND ig.rgt <= %(rgt)s
            AND i.disabled = 0
            AND (
                i.name LIKE %(txt)s
                OR i.item_name LIKE %(txt)s
            )
        ORDER BY
            i.name
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "lft": group_bounds.lft,
            "rgt": group_bounds.rgt,
            "txt": f"%{txt}%",
            "start": start,
            "page_len": page_len,
        },
        as_dict=True,
    )
