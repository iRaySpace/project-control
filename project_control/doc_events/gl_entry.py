import frappe


# Fix for Non-PL (project not set)
def validate(doc, method):
    if doc.voucher_type == 'Sales Invoice':
        doc.project = frappe.db.get_value('Sales Invoice', doc.voucher_no, 'project')
