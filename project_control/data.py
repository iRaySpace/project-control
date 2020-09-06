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


def _get_ignore_se():
    return frappe.db.get_single_value('Project Control Settings', 'ignore_se')
