# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = _get_columns(filters), _get_data(filters)
	print(data)
	return columns, data


def _get_columns(filters):
	def make_column(label, fieldname, width, fieldtype='Data', options=''):
		return {
			'label': _(label),
			'fieldname': fieldname,
			'width': width,
			'fieldtype': fieldtype,
			'options': options
		}
	return [
		make_column('Project Code', 'project_code', 110),
		make_column('Project Name', 'project_name', 180),
		make_column('Sales', 'sales', 130, 'Currency'),
		make_column('Budget', 'budget', 130, 'Currency'),
		make_column('Estimated GP', 'estimated_gp', 130, 'Currency'),
		make_column('Remaining Diff', 'remaining_diff', 130, 'Currency'),
		make_column('Unbilled Amount', 'unbilled_amount', 130, 'Currency'),
		make_column('Billing Amount', 'billing_amount', 130, 'Currency')
	]


def _get_data(filters):
	def make_data(row):
		remaining_diff = row.get('sales') - row.get('total_billed_amount')
		unbilled_amount = remaining_diff * (row.get('pc_per_unbilled') / 100.00)
		billing_amount = remaining_diff - unbilled_amount
		return {
			**row,
			'remaining_diff': remaining_diff,
			'unbilled_amount': unbilled_amount,
			'billing_amount': billing_amount
		}

	data = frappe.db.sql("""
		SELECT
			name as project_code,
			project_name,
			total_sales_amount as sales,
			pc_estimated_total as budget,
			pc_estimated_gross_margin as estimated_gp,
			total_billed_amount,
			pc_per_unbilled
		FROM `tabProject`
	""", as_dict=1)

	return list(map(make_data, data))
