from functools import reduce
import frappe
from frappe import _
from project_control.data import calculate_estimated_gross_margin


def validate(project, method):
    _validate_installation_note(project)
    _set_budget_total(project)
    _set_variation_total(project)
    _set_estimated_total(project)


# TODO: dynamic via Settings
def after_insert(project, method):
    tasks = [
        'Advance Payment',
        'Supplier LPO',
        'Supplier Payment',
        'Custom Clearance & Payment',
        'Receive Goods',
        'Delivery',
        'Installation',
        'Payment'
    ]
    for task in tasks:
        frappe.get_doc({
            'doctype': 'Task',
            'subject': task,
            'project': project.name
        }).insert()
    frappe.msgprint(_('Tasks are also generated.'))


def _validate_installation_note(project):
    in_validation = frappe.db.get_single_value('Project Control Settings', 'in_validation')
    if in_validation and project.status == 'Completed':
        installation_notes = frappe.get_all('Installation Note', {'project': project.name})
        if not installation_notes:
            frappe.throw(_('Please make an Installation Note first before closing the project'.format(project.name)))


def _set_budget_total(project):
    budget_total = reduce(lambda total, budget: total + budget.amount, project.pc_budgets, 0.0)
    project.pc_budget_total = budget_total


def _set_variation_total(project):
    variation_total = reduce(lambda total, budget: total + budget.amount, project.pc_variations, 0.0)
    project.pc_variation_total = variation_total


def _set_estimated_total(project):
    project.pc_estimated_total = sum([project.pc_budget_total, project.pc_variation_total])
    if not project.estimated_costing:
        project.estimated_costing = project.pc_estimated_total
    estimated_gross_margin, estimated_gross_margin_per = calculate_estimated_gross_margin(project)
    project.pc_estimated_gross_margin = estimated_gross_margin
    project.pc_estimated_gross_margin_per = estimated_gross_margin_per
