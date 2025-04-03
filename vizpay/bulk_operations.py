# Copyright (c) 2025, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _

@frappe.whitelist()
def fetch_statuses_in_background(transactions, doctype):
	transactions = frappe.parse_json(transactions)
	progress = 1
	completion = len(transactions)
	frappe.msgprint(
		_("Creating A Background Job to Fetch {0} Status(s)").format(len(transactions)),
		alert=True
	)

	for transaction in transactions:
		frappe.enqueue(
			method=fetch_status,
			queue="default",
			transaction_name=transaction.get("name", None)
		)
		percentage = (progress/completion) * 100
		frappe.publish_progress(
			percentage,
			title="Fetching Status(s)",
			description=f"Row #{progress}: Fetching Status",
			doctype=doctype
		)
		progress += 1

	progress = 1


def fetch_status(transaction_name):
	doc = frappe.get_doc("Vizpay Transaction", transaction_name)
	try:
		status = doc.fetch_transaction_status()
	except Exception as e:
		frappe.log_error("Bulk Status Fetching Failed!", frappe.get_traceback())
		return 1
	