import frappe


# Fix for Non-PL (project not set)
def validate(doc, method):
    voucher_type = doc.voucher_type
    if voucher_type in ['Sales Invoice', 'Delivery Note']:
        doc.project = frappe.db.get_value(voucher_type, doc.voucher_no, 'project')
