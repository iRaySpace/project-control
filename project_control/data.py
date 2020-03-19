import frappe
from frappe import _


def validate_project_costing(project, cost):
    estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
    total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')
    if total_purchase_cost + cost > estimated_total:
        frappe.throw(_('Transaction is not allowed. Total purchase cost will exceed project estimated value.'))
