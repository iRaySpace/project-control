# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.report.general_ledger import general_ledger


def execute(filters=None):
	general_ledger.get_gl_entries = _get_gl_entries
	col, res = general_ledger.execute(filters)

	# empty_project_rows = _filter_rows_of_empty_project(res)
	# distinct_documents = _filter_rows_of_similar_documents(empty_project_rows)
	# vouchers_with_project = _get_vouchers_with_project(distinct_documents)

	# return col, _set_res_with_projects(res, vouchers_with_project)
	return col, res


def _get_gl_entries(filters):
	currency_map = get_currency(filters)
	select_fields = """, debit, credit, debit_in_account_currency,
			credit_in_account_currency """

	order_by_statement = "order by je.posting_date, jea.account, jea.creation"

	if filters.get("group_by") == _("Group by Voucher"):
		order_by_statement = "order by posting_date, voucher_type, voucher_no"

	if filters.get("include_default_book_entries"):
		filters['company_fb'] = frappe.db.get_value("Company", filters.get("company"), 'default_finance_book')

	gl_entries = frappe.db.sql(
		"""
        SELECT
            jea.name as gl_entry,
            je.posting_date,
            jea.account,
            jea.party_type,
            jea.party,
            jea.reference_type as against_voucher_type,
            jea.reference_name as against_voucher,
            jea.cost_center, 
            jea.project,
            jea.account_currency,
            jea.user_remark as remarks,
            jea.against_account as against {select_fields}
        FROM `tabJournal Entry Account` jea
        INNER JOIN `tabJournal Entry` je ON jea.parent = je.name
        WHERE je.company=%(company)s AND je.docstatus=1 {conditions}
        {order_by_statement}
        """.format(
			select_fields=select_fields,
			conditions=general_ledger.get_conditions(filters),
			order_by_statement=order_by_statement
		), filters, as_dict=1)

	if filters.get('presentation_currency'):
		return convert_to_presentation_currency(gl_entries, currency_map)
	else:
		return gl_entries


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
		elif voucher_type == 'Journal Entry':
			voucher = frappe.db.sql("""
				SELECT 
					jea.project 
				FROM `tabJournal Entry` je
				INNER JOIN `tabJournal Entry Account` jea
				ON je.name = jea.parent
				WHERE je.name = %s
				AND jea.project != '' 
			""", voucher_no, as_dict=1)
			if voucher:
				voucher_project = voucher[0].get('project')
				vouchers_with_project[voucher_no] = voucher_project

	return vouchers_with_project


def _set_res_with_projects(res, vouchers_with_project):
	for data in res:
		voucher_no = data.get('voucher_no')
		if voucher_no in vouchers_with_project:
			data['project'] = vouchers_with_project[voucher_no]
	return res


# def _get_journal_entries():
# 	journal_entries = frappe.db.sql("""
# 		SELECT
# 			account,
# 			party_type,
# 			party,
# 			against_account,
# 			debit,
# 			credit,
# 			account_currency,
# 			debit_in_account_currency,
# 			credit_in_account_currency,
# 			reference_type,
# 			reference_name,
# 			user_remark,
# 			cost_center,
# 			project
# 		FROM `tabJournal Entry Account`
# 		WHERE docstatus=1
# 	""", as_dict=1)
# 	print(journal_entries)
