# Copyright (c) 2025, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from vizpay.utils import log_and_structure


@frappe.whitelist(methods=["GET"])
@log_and_structure
def get_terminals():
    return frappe.db.get_all("Vizpay Terminal", fields=["name", "terminal_name"])
