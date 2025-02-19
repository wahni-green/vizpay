// Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vizpay Transaction", {
	refresh(frm) {
        frm.add_custom_button(__('Fetch Status'), function() {
            frm.call("fetch_transaction_status");
        });
	},
});
