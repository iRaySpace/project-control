from functools import reduce
import frappe
from frappe import _


def validate(project, method):
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


def _set_budget_total(project):
    budget_total = reduce(lambda total, budget: total + budget.amount, project.pc_budgets, 0.0)
    project.pc_budget_total = budget_total


def _set_variation_total(project):
    variation_total = reduce(lambda total, budget: total + budget.amount, project.pc_variations, 0.0)
    project.pc_variation_total = variation_total


def _set_estimated_total(project):
    project.pc_estimated_total = sum([project.pc_budget_total, project.pc_variation_total])
