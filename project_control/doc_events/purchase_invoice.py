import frappe
from frappe import _


def validate(invoice, method):
    for item in invoice.items:
        _validate_project_costing(item)


def _validate_project_costing(item):
    project = item.project
    if project:
        estimated_total = frappe.get_value('Project', project, 'pc_estimated_total')
        total_purchase_cost = frappe.get_value('Project', project, 'total_purchase_cost')
        if total_purchase_cost + item.amount > estimated_total:
            frappe.throw(_('Transaction is not allowed. Total purchase cost will exceeds project estimated value.'))
