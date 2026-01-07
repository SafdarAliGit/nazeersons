frappe.ui.form.on("Item", {
    refresh(frm) {
        // Set filter
        frm.set_query('item', 'custom_item_recipe', function() {
            return {
                filters: {
                    'item_group': ['descendants of', 'Raw Material'],
                    'disabled': 0
                }
            };
        });
        
        // Add validation when item is selected
        frm.fields_dict['custom_item_recipe'].grid.wrapper.on('grid-row-render', function(e, grid_row) {
            let item_field = grid_row.get_field('item');
            if (item_field) {
                item_field.df.onchange = function() {
                    if (this.value) {
                        frappe.db.get_value('Item', this.value, 'item_group')
                            .then(r => {
                                if (r.message) {
                                    // Check if item group is under Raw Material
                                    frappe.call({
                                        method: 'frappe.client.get_list',
                                        args: {
                                            doctype: 'Item Group',
                                            filters: [
                                                ['name', '=', r.message.item_group],
                                                ['name', 'descendants of', 'Raw Material']
                                            ],
                                            limit: 1
                                        },
                                        callback: function(response) {
                                            if (!response.message || response.message.length === 0) {
                                                frappe.msgprint(__('Only Raw Material items are allowed'));
                                                frappe.model.set_value(grid_row.doctype, grid_row.docname, 'item', '');
                                            }
                                        }
                                    });
                                }
                            });
                    }
                };
            }
        });
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