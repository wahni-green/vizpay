// Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
// For license information, please see license.txt

frappe.listview_settings["Vizpay Transaction"] = {
    onload: function(listview) {
        frappe.realtime.on('rq_job_error', (data) => {
            if (data) {
                frappe.throw(__(
                    `Background Job for Fetching Status(s) Failed.
                    Please Check Error Log for More Details.`
                ))
            }
        })
        listview.page.add_action_item(__("Fetch Statuses"), () => {
            let checked_items = listview.get_checked_items()
            if (checked_items[0]) {
                frappe
                frappe.confirm(
                    __("Fetch Status of {0} Vizpay Transaction(s)?", [checked_items.length]), () => {
                        frappe.call({
                            method: "vizpay.bulk_operations.fetch_statuses_in_background",
                            args: {
                                "transactions": checked_items,
                                "doctype": listview.doctype,
                            },
                            callback: function(r) {
                                if (!r) {
                                    frappe.realtime.off("rq_job_error")
                                }
                            }
                        })
                    }
                )
            } else {
                frappe.throw(__("Please Select Transactions"))
            }
        })
    }
}
