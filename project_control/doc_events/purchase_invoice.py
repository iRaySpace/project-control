import frappe
from frappe import _
from project_control.data import validate_project_costing


def validate(invoice, method):
    _validate_multiple_projects(invoice)
    _set_project_field(invoice)
    _set_items_project_field(invoice)
    if invoice.project:
        validate_project_costing(invoice.project, invoice.base_grand_total)


def _validate_multiple_projects(invoice):
    projects = list(
        set(
            filter(
                lambda x: x,
                map(lambda x: x.project, invoice.items)
            )
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
        if projects:
            invoice.project = projects[0]


def _set_items_project_field(invoice):
    if invoice.project:
        for item in invoice.items:
            item.project = invoice.project
