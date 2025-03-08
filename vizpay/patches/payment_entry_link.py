# Copyright (c) 2024, Wahni IT Solutions Pvt Ltd and contributors
# For license information, please see license.txt

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Payment Entry": [
				{
					"fieldname": "vizpay_transaction",
					"label": "Vizpay Transaction",
					"fieldtype": "Link",
					"options": "Vizpay Transaction",
					"insert_after": "reference_no",
					"translatable": 0,
					"read_only": 1,
				},
			],
        }
    )