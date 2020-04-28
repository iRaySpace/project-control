# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from project_control.api.project import get_journal_costs, get_delivery_note_costs


def execute(filters=None):
	columns, data = _get_columns(filters), _get_data(filters)
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
		make_column('Sales Invoice', 'sales_invoice', 130, 'Currency'),
		make_column('Purchase Invoice', 'purchase_invoice', 130, 'Currency'),
		make_column('Delivery Note', 'delivery_note', 130, 'Currency'),
		make_column('Stock Issued', 'stock_issued', 130, 'Currency'),
		make_column('JV', 'journal_voucher', 130, 'Currency')
	]


def _get_data(filters):
	projects = frappe.db.sql("""
		SELECT
			name as project_code,
			project_name,
			total_sales_amount as sales_invoice,
			total_purchase_cost as purchase_invoice,
			total_consumed_material_cost as stock_issued
		FROM `tabProject`
	""", as_dict=1)
	for project in projects:
		project['delivery_note'] = get_delivery_note_costs(project.get('project_code'))
		project['journal_voucher'] = get_journal_costs(project.get('project_code'))
	return projects
