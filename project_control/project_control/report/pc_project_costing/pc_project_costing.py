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
	def make_column(label, fieldname, width, fieldtype='Currency', options=''):
		return {
			'label': _(label),
			'fieldname': fieldname,
			'width': width,
			'fieldtype': fieldtype,
			'options': options
		}
	return [
		make_column('Project Code', 'project_code', 110, 'Data'),
		make_column('Project Name', 'project_name', 180, 'Data'),
		make_column('Sales Invoice', 'sales_invoice', 130),
		make_column('Purchase Invoice', 'purchase_invoice', 130),
		make_column('Delivery Note', 'delivery_note', 130),
		make_column('Stock Issued', 'stock_issued', 130),
		make_column('JV', 'journal_voucher', 130),
		make_column('WIP Billing', 'wip_billing', 130),
		make_column('WIP Job Cost', 'wip_job_cost', 130),
		make_column('Total', 'total', 130)
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

	wip_billing_account = _get_wip_billing_account()
	wip_job_cost_account = _get_wip_job_cost_account()

	for project in projects:
		project_code = project.get('project_code')
		stock_issued = project.get('stock_issued')

		delivery_note = get_delivery_note_costs(project_code)
		journal_voucher = get_journal_costs(project_code)

		wip_billing = sum([
			project.get('sales_invoice'),
			_get_net_journal(project_code, wip_billing_account)
		])

		wip_job_cost = sum([
			delivery_note,
			stock_issued,
			_get_net_journal(project_code, wip_job_cost_account),
			_get_purchase_invoice_costs(project_code, wip_job_cost_account)
		])

		project['delivery_note'] = delivery_note
		project['journal_voucher'] = journal_voucher
		project['wip_billing'] = wip_billing
		project['wip_job_cost'] = wip_job_cost
		project['total'] = wip_billing + wip_job_cost

	return projects


def _get_net_journal(project, account):
	net_journal = 0.0
	data = frappe.db.sql("""
		SELECT 
			SUM(debit_in_account_currency) as total_debit,
			SUM(credit_in_account_currency) as total_credit
		FROM `tabJournal Entry Account`
		WHERE docstatus=1
		AND project=%s
		AND account=%s
	""", (project, account), as_dict=1)
	if data:
		total_debit = data[0].get('total_debit') or 0.0
		total_credit = data[0].get('total_credit') or 0.0
		net_journal = total_debit - total_credit
	return net_journal


def _get_wip_billing_account():
	wip_billing = frappe.db.get_single_value('Project Control Settings', 'wip_billing_account')
	if not wip_billing:
		frappe.throw(_('WIP Billing Account is not set. Please set it under Project Control Settings.'))
	return wip_billing


def _get_wip_job_cost_account():
	wip_job_cost = frappe.db.get_single_value('Project Control Settings', 'wip_job_cost_account')
	if not wip_job_cost:
		frappe.throw(_('WIP Job Cost Account is not set. Please set it under Project Control Settings.'))
	return wip_job_cost


def _get_purchase_invoice_costs(project, account):
	purchase_invoice_costs = 0.0
	data = frappe.db.sql("""
			SELECT SUM(amount) as total_costs
			FROM `tabPurchase Invoice Item`
			WHERE docstatus=1
			AND project=%s
			AND expense_account=%s
		""", (project, account), as_dict=1)
	if data:
		purchase_invoice_costs = data[0].get('total_costs') or 0.0
	return purchase_invoice_costs
