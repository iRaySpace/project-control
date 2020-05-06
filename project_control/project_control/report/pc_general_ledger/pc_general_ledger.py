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

	order_by_statement = "order by posting_date, account, creation"

	if filters.get("group_by") == _("Group by Voucher"):
		order_by_statement = "order by posting_date, voucher_type, voucher_no"

	if filters.get("include_default_book_entries"):
		filters['company_fb'] = frappe.db.get_value("Company", filters.get("company"), 'default_finance_book')

	gl_entries = frappe.db.sql(
		"""
		SELECT
			posting_date, account, party_type, party,
			voucher_type, voucher_no, cost_center, project,
			against_voucher_type, against_voucher, account_currency,
			remarks, against, is_opening {select_fields}
		FROM `tabGL Entry`
		WHERE company=%(company)s
		AND voucher_type != 'Journal Entry' {conditions}
		{order_by_statement}
		""".format(
			select_fields=select_fields,
			conditions=general_ledger.get_conditions(filters),
			order_by_statement=order_by_statement
		), filters, as_dict=1)

	je_order_by_statement = "order by je.posting_date, jea.account, jea.creation"

	if filters.get("group_by") == _("Group by Voucher"):
		je_order_by_statement = "order by je.posting_date, je.name"

	je_conditions = _get_conditions(filters, True)

	journal_entries = frappe.db.sql(
		"""
        SELECT
            jea.name as gl_entry,
            je.posting_date,
            jea.account,
            'Journal Entry' as voucher_type,
            je.name as voucher_no,
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
			conditions=je_conditions,
			order_by_statement=je_order_by_statement
		), filters, as_dict=1)

	print('hala')

	entries = [*gl_entries, *journal_entries]

	if filters.get('presentation_currency'):
		return convert_to_presentation_currency(entries, currency_map)
	else:
		return entries


def _get_conditions(filters, je=False):
	conditions = general_ledger.get_conditions(filters)
	if je:
		conditions = conditions.replace('voucher_no', 'je.name', 1)
	return conditions
