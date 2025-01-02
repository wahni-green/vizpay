# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests


class Vizpay:
    def __init__(self):
        self.settings = frappe.get_single("Vizpay Settings")
        if not self.settings.enabled:
            frappe.throw(_("Vizpay is disabled"))

    def push_transaction(self, transaction):
        payload = {
            "mid": self.settings.merchant_id,
            "tid": transaction.terminal,
            "tran_type": self.settings.transaction_type,
            "amount": transaction.amount,
            "bill_no": str(transaction.bill_no or ""),
            "tip": transaction.tip,
            "erp_tran_id": transaction.name,
            "erp_client_id": "ajshdsbdchsallje29ewurfhdjcm",
            "source_id":"ajshdsbdchsallje29ewurfhdjcm",
        }

        url = f"{self.settings.base_url}/erpservice/ERP/PushTxn"
        response = requests.post(url, json=payload)
        frappe.msgprint(
            str(response.json()), title="Vizpay Transaction Response"
        )


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_transaction_status(**kwargs):
    frappe.log_error(message=str(kwargs), title="Vizpay Transaction Status Update")
    if not kwargs.get("ErpTranId"):
        frappe.log_error(message=str(kwargs), title="Vizpay Transaction Status Update - No Transaction ID")

    transaction = frappe.get_doc("Vizpay Transaction", kwargs.get("ErpTranId"))
    if not transaction:
        frappe.log_error(message=str(kwargs), title="Vizpay Transaction Status Update - Missing Transaction")

    transaction.update_transaction_status(pretty_json(kwargs))
    return


def pretty_json(obj):
	if not obj:
		return ""

	if isinstance(obj, str):
		return obj

	return frappe.as_json(obj, indent=4)


def log_and_structure(func):
    def wrapper(*args, **kwargs):
        cmd = kwargs.get("cmd")
        try:
            kwargs = frappe.get_newargs(func, kwargs)
            return {"status": True, "message": func(*args, **kwargs)}
        except Exception as e:
            frappe.log_error(
                title=f"Vizpay API Error: {cmd or func.__name__}",
                message=frappe.get_traceback(),
            )
            return {"status": False, "error": str(e)}

    return wrapper
