frappe.ui.form.on("Item", {
    refresh(frm) {
        
    frm.fields_dict['custom_item_recipe'].grid.get_field('item').get_query = function() {
                 return {
                    query: 'nazeersons.nazeersons.utils.recipe_items_filter.recipe_items_filter'
                 };
            };
        

        }
});

frappe.ui.form.on('Item Recipe', {
    item: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.item) {
            // Optionally pass warehouse if you have it in parent or row
            let warehouse = frm.doc.default_warehouse || null;  
            frappe.call({
                method: 'nazeersons.nazeersons.utils.get_item_valuation_rate.get_item_valuation_rate',
                args: {
                    item_code: row.item,
                    warehouse: warehouse
                },
                callback: function(r) {
                    if (!r.exc && r.message !== undefined) {
                        // set the rate field in this child row
                        frappe.model.set_value(cdt, cdn, 'rate', r.message);
                        frappe.model.set_value(cdt, cdn, 'amount', r.message * row.qty);
                    }
                }
            });
        } else {
            // if item_code cleared, also clear rate
            frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
    },
    qty: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.qty) {
            frappe.model.set_value(cdt, cdn, 'amount', row.rate * row.qty);
        }
    }
});