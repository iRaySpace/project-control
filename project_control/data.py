import frappe
from frappe import _


def validate_project_costing(project, cost, stock_item_issue=False):
    estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
    total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')

    total_costing = sum([total_purchase_cost, cost])
    if not _get_ignore_se() or stock_item_issue:
        total_consumed_material_cost = frappe.get_value('Project', project, 'total_consumed_material_cost')
        total_costing = total_costing + total_consumed_material_cost

    if total_costing > estimated_total:
        frappe.throw(_('Transaction is not allowed. Total purchase cost will exceed project estimated value.'))


def validate_project_costing_for_warning(project, cost):
    estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
    total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')

    total_costing = sum([total_purchase_cost, cost])
    if not _get_ignore_se():
        total_consumed_material_cost = frappe.get_value('Project', project, 'total_consumed_material_cost')
        total_costing = total_costing + total_consumed_material_cost

    if total_costing > estimated_total:
        frappe.msgprint(_('Total purchase cost will exceed project estimated value.'))


def calculate_estimated_gross_margin(data):
    basis_values = sum([data.get(x) for x in _get_estimated_base_on()])
    estimated_costing = data.get('estimated_costing')
    estimated_profit = basis_values - estimated_costing
    estimated_profit_per = (estimated_profit / basis_values) * 100 if basis_values else 0.00
    return estimated_profit, estimated_profit_per


def _get_ignore_se():
    return frappe.db.get_single_value('Project Control Settings', 'ignore_se')


def _get_estimated_base_on():
    estimated_base_on = frappe.db.get_single_value('Project Control Settings', 'estimated_base_on')
    if not estimated_base_on:
        frappe.throw(_('Please set Estimated Base On under Project Control Settings'))
    fields = {
        'Order Value': ['pc_order_value'],
        'Sales Amount': ['total_sales_amount'],
        'Billed Amount': ['total_billed_amount'],
        'Sales and Billed Amount': ['total_sales_amount', 'total_billed_amount']
    }
    return fields[estimated_base_on]
