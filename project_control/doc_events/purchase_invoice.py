import frappe
from frappe import _
from project_control.data import validate_project_costing


def validate(invoice, method):
    _validate_multiple_projects(invoice)
    _set_project_field(invoice)
    _set_items_project_field(invoice)
    for item in invoice.items:
        if item.project:
            validate_project_costing(item.project, item.amount)


def _validate_multiple_projects(invoice):
    projects = list(
        filter(
            lambda x: x,
            map(lambda x: x.project, invoice.items)
        )
    )
    if len(projects) > 1:
        frappe.throw(_('Please set only one Project per Invoice.'))


def _set_project_field(invoice):
    if not invoice.project:
        projects = list(
            filter(
                lambda x: x,
                map(lambda x: x.project, invoice.items)
            )
        )
        invoice.project = projects[0]


def _set_items_project_field(invoice):
    if invoice.project:
        for item in invoice.items:
            item.project = invoice.project
