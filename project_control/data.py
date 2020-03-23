import frappe
from frappe import _


def validate_project_costing(project, cost):
    estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
    total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')
    total_consumed_material_cost = frappe.get_value('Project', project, 'total_consumed_material_cost')

    total_costing = total_purchase_cost + total_consumed_material_cost
    if total_costing + cost > estimated_total:
        frappe.throw(_('Transaction is not allowed. Total purchase cost will exceed project estimated value.'))


def validate_project_costing_for_warning(project, cost):
    estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
    total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')
    total_consumed_material_cost = frappe.get_value('Project', project, 'total_consumed_material_cost')

    total_costing = total_purchase_cost + total_consumed_material_cost
    if total_costing + cost > estimated_total:
        frappe.msgprint(_('Total purchase cost will exceed project estimated value.'))
