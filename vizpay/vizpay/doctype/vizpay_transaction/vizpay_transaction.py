# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from vizpay.utils import Vizpay


class VizpayTransaction(Document):
	def validate(self):
		self.status = "Pending"

	def after_insert(self):
		vizpay = Vizpay()
		resp = vizpay.push_transaction(self)
		self.add_comment(text=str(resp))

	def update_transaction_status(self, response):
		self.response = response
		if response.get("TxnStatus") == "SUCCESS":
			self.status = "Success"
		else:
			self.status = "Failed"
		self.db_update()

	def mark_payment_as_complete(self):
		# link payment entry and submit it
		pass
