# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.utils import today
from frappe.model.document import Document

from erpnext import get_default_company
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_entry.payment_entry import (
    get_bank_cash_account,
)

from vizpay.utils import Vizpay, pretty_json


class VizpayTransaction(Document):
	def validate(self):
		self.status = "Pending"

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
			self.mark_payment_as_complete()
		else:
			self.status = "Failed"
		self.db_update()

	def mark_payment_as_complete(self):
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

		payment_entry = frappe.new_doc("Payment Entry")
		payment_entry.payment_type = "Receive"
		payment_entry.posting_date = today()
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

		payment_entry.reference_no = self.name
		payment_entry.reference_date = payment_entry.posting_date

		payment_entry.setup_party_account_field()
		payment_entry.set_missing_values()
		payment_entry.save()

		payment_entry.submit()
