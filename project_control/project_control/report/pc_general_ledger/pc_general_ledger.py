# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.general_ledger import general_ledger


def execute(filters=None):
	col, res = general_ledger.execute(filters)

	empty_project_rows = _filter_rows_of_empty_project(res)
	distinct_documents = _filter_rows_of_similar_documents(empty_project_rows)
	vouchers_with_project = _get_vouchers_with_project(distinct_documents)

	return col, _set_res_with_projects(res, vouchers_with_project)


def _filter_rows_of_empty_project(rows):
	def make_data(row):
		return row.get('voucher_type') and row.get('voucher_no') and not row.get('project')

	return list(filter(make_data, rows))


def _filter_rows_of_similar_documents(empty_project_rows):
	data = []

	def filter_from_data(row):
		return list(filter(
			lambda x:
			x['voucher_type'] == row['voucher_type']
			and x['voucher_no'] == row['voucher_no'], data))

	for empty_project_row in empty_project_rows:
		existing = filter_from_data(empty_project_row)
		if not existing:
			data.append(empty_project_row)

	return data


def _get_vouchers_with_project(distinct_documents):
	vouchers_with_project = {}
	for document in distinct_documents:
		voucher_no = document.get('voucher_no')
		voucher_type = document.get('voucher_type')
		if voucher_type == 'Sales Invoice':
			vouchers_with_project[voucher_no] = frappe.db.get_value('Sales Invoice', voucher_no, 'project')
		elif voucher_type == 'Purchase Invoice':
			vouchers_with_project[voucher_no] = frappe.db.get_value('Purchase Invoice', voucher_no, 'project')
		elif voucher_type == 'Stock Entry':
			vouchers_with_project[voucher_no] = frappe.db.get_value('Stock Entry', voucher_no, 'project')
	return vouchers_with_project


def _set_res_with_projects(res, vouchers_with_project):
	for data in res:
		voucher_no = data.get('voucher_no')
		if voucher_no in vouchers_with_project:
			data['project'] = vouchers_with_project[voucher_no]
	return res
