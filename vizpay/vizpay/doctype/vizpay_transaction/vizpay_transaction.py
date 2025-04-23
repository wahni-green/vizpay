# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.utils import today, getdate
from frappe.model.document import Document

from erpnext import get_default_company
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	get_bank_cash_account,
)

from vizpay.utils import Vizpay, pretty_json


class VizpayTransaction(Document):
	def validate(self):
		if self.is_new():
			self.status = "Pending"
		self.bill_no = self.name

	def after_insert(self):
		vizpay = Vizpay()
		resp = vizpay.push_transaction(self)
		self.add_comment(text=str(resp))

	@frappe.whitelist()
	def fetch_transaction_status(self):
		vizpay = Vizpay()
		resp = vizpay.get_transaction_status(self)
		self.update_transaction_status(pretty_json(resp))
		frappe.msgprint("Transaction Status Updated")

	def update_transaction_status(self, response):
		self.response = response
		response = json.loads(response)
		if response.get("ResponseCode") == "00":
			self.status = "Success"
			reference_no = response.get("RspData", {}).get("TranId")
			txn_completion_date = response.get("RspData", {}).get("TxnCompletionDate")
			self.mark_payment_as_complete(reference_no, txn_completion_date)
		else:
			self.status = "Failed"
		self.db_update()

	def mark_payment_as_complete(self, reference_no=None, txn_completion_date=None):
		if frappe.db.get_value(
			"Payment Entry",
			{
				"reference_no": self.name,
				"docstatus": 1,
				"payment_type": "Receive",
				"party_type": "Customer",
				"party": self.customer,
				"paid_amount": self.amount,
			}
		):
			return

		is_frozen = frappe.db.get_value("Customer", self.customer, "is_frozen")

		if is_frozen:
			frappe.db.set_value("Customer", self.customer, "is_frozen", 0)

		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Receive"
		payment_entry.posting_date = txn_completion_date or today()
		payment_entry.mode_of_payment = frappe.get_single("Vizpay Settings").mode_of_payment
		payment_entry.party_type = "Customer"
		payment_entry.party = self.customer
		payment_entry.company = get_default_company()

		payment_entry.paid_amount = self.amount
		payment_entry.received_amount = payment_entry.paid_amount

		bank = get_bank_cash_account(payment_entry, None)
		party_account = get_party_account(
			payment_entry.party_type, payment_entry.party, payment_entry.company
		)
		payment_entry.paid_from = party_account
		payment_entry.paid_to = bank.account

		payment_entry.vizpay_transaction = self.name
		payment_entry.reference_no = reference_no or self.name
		payment_entry.reference_date = payment_entry.posting_date

		payment_entry.setup_party_account_field()
		payment_entry.set_missing_values()

		payment_entry.flags.ignore_permissions = True
		payment_entry.save()
		payment_entry.submit()

		if is_frozen:
			frappe.db.set_value("Customer", self.customer, "is_frozen", 1)
