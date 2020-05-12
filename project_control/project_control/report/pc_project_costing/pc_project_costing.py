# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr
from project_control.api.project import get_delivery_note_costs


def execute(filters=None):
	_validate_filters(filters)
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
		make_column('Old Serial No', 'old_serial_no', 130, 'Data'),
		make_column('Project Name', 'project_name', 180, 'Data'),
		make_column('Order Value', 'order_value', 130),
		make_column('WIP Billing', 'wip_billing', 130),
		make_column('Estimated Cost', 'estimated_cost', 130),
		make_column('WIP Job Cost', 'wip_job_cost', 130)
	]


def _get_data(filters):
	projects = frappe.db.sql("""
		SELECT
			name as project_code,
			project_name,
			total_sales_amount as sales_invoice,
			total_purchase_cost as purchase_invoice,
			total_consumed_material_cost as stock_issued,
			pc_order_value as order_value,
			old_serial_no,
			pc_estimated_total as estimated_cost
		FROM `tabProject`
		{conditions}
	""".format(
		conditions=_get_conditions(filters)
	), filters, as_dict=1)

	wip_billing_account = _get_wip_billing_account()
	wip_job_cost_account = _get_wip_job_cost_account()

	for project in projects:
		project_code = project.get('project_code')
		stock_issued = project.get('stock_issued')

		delivery_note = get_delivery_note_costs(
			project_code,
			_get_posting_date_conditions(),
			filters
		)

		wip_billing = sum([
			project.get('sales_invoice'),
			_get_net_journal(
				project_code,
				wip_billing_account,
				_get_posting_date_conditions(),
				filters
			)
		])

		wip_job_cost = sum([
			delivery_note,
			stock_issued,
			_get_net_journal(
				project_code,
				wip_job_cost_account,
				_get_posting_date_conditions(),
				filters
			),
			_get_purchase_invoice_costs(
				project_code,
				wip_job_cost_account,
				_get_posting_date_conditions(),
				filters
			)
		])

		project['wip_billing'] = wip_billing
		project['wip_job_cost'] = wip_job_cost

	return projects


def _validate_filters(filters):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	# would not work on v12 (probably)
	if filters.get('project'):
		projects = cstr(filters.get("project")).strip()
		filters.project = [d.strip() for d in projects.split(',') if d]


def _get_conditions(filters):
	conditions = []
	if filters.get('project'):
		conditions.append('name IN %(project)s')
	return 'WHERE {}'.format(' AND '.join(conditions)) if conditions else ''


def _get_posting_date_conditions():
	return 'posting_date >= %(from_date)s AND posting_date <= %(to_date)s'


def _get_net_journal(project, account, conditions='', filters={}):
	filters['project'] = project
	filters['account'] = account

	if conditions:
		conditions = 'AND {}'.format(conditions)

	net_journal = 0.0
	data = frappe.db.sql("""
		SELECT 
			SUM(jea.debit_in_account_currency) as total_debit,
			SUM(jea.credit_in_account_currency) as total_credit
		FROM `tabJournal Entry Account` jea
		INNER JOIN `tabJournal Entry` je
		ON jea.parent = je.name
		WHERE je.docstatus=1
		AND jea.project=%(project)s
		AND jea.account=%(account)s
		{conditions}
	""".format(conditions=conditions), filters, as_dict=1)

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


def _get_purchase_invoice_costs(project, account, conditions='', filters={}):
	filters['project'] = project
	filters['account'] = account

	if conditions:
		conditions = 'AND {}'.format(conditions)

	purchase_invoice_costs = 0.0
	data = frappe.db.sql("""
			SELECT SUM(pii.amount) as total_costs
			FROM `tabPurchase Invoice Item` pii
			INNER JOIN `tabPurchase Invoice` pi
			ON pii.parent = pi.name
			WHERE pii.docstatus=1
			AND pii.project=%(project)s
			AND pii.expense_account=%(account)s
			{conditions}
		""".format(conditions=conditions), filters, as_dict=1)

	if data:
		purchase_invoice_costs = data[0].get('total_costs') or 0.0

	return purchase_invoice_costs
