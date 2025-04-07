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
		_("Creating Background Jobs to Fetch Status of {0} Transactions").format(len(transactions)),
		alert=True
	)

	# enqueue fetching status
	for transaction in transactions:
		frappe.enqueue(
			method=fetch_status,
			queue="default",
			transaction_name=transaction.get("name", None),
		)
		# display percentage of completion
		percentage = (progress/completion) * 100
		frappe.publish_progress(
			percentage,
			title="Fetching Status(s)",
			description=f"Row #{progress}: Fetching Status",
			doctype=doctype,
		)
		progress += 1

	progress = 1


def fetch_status(transaction_name):
	doc = frappe.get_doc("Vizpay Transaction", transaction_name)
	doc.fetch_transaction_status()


def fetch_status_for_pending():
	pending_transactions = frappe.db.get_all("Vizpay Transaction", {"status": "Pending"})

	if not pending_transactions:
		return

	for transaction in pending_transactions:
		frappe.enqueue(
			method=fetch_status,
			queue="default",
			transaction_name=transaction.get("name", None),
		)