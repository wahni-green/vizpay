# Copyright (c) 2025, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from vizpay.utils import log_and_structure


@frappe.whitelist(allow_guest=True, methods=["POST"])
@log_and_structure
def create_transaction(customer, amount, terminal, bill_no, pay_type=1):
    transaction = frappe.get_doc(
        {
            "doctype": "Vizpay Transaction",
            "customer": customer,
            "amount": amount,
            "terminal": terminal,
            "bill_no": bill_no,
            "transaction_type": pay_type,
        }
    )
    transaction.insert(ignore_permissions=True)
    return "Transaction Initiated Successfully"


@frappe.whitelist(methods=["GET"])
@log_and_structure
def get_transaction(transaction_id):
    return frappe.get_doc("Vizpay Transaction", transaction_id).as_dict()


@frappe.whitelist(methods=["GET"])
@log_and_structure
def get_pending_transactions():
    return frappe.get_list(
        "Vizpay Transaction",
        filters={"status": "Pending"},
        fields=["name", "amount", "terminal", "bill_no", "customer"],
    )


@frappe.whitelist(methods=["GET"])
@log_and_structure
def get_transactions(filters=None, start=0, limit=20):
    if not filters:
        filters = {}

    return frappe.get_list(
        "Vizpay Transaction",
        filters=filters,
        fields=[
            "name", "amount", "terminal",
            "bill_no", "customer", "status"
        ],
        order_by="creation desc",
        start=start,
        page_length=limit,
    )


@frappe.whitelist(methods=["GET"])
@log_and_structure
def check_transaction_status(transaction_id):
    return frappe.db.get_value("Vizpay Transaction", transaction_id, "status")


@frappe.whitelist(methods=["GET"])
@log_and_structure
def get_terminals():
    return frappe.db.get_all("Vizpay Terminal", pluck="name")
