import frappe


def execute():
    gl_entries = frappe.db.get_all(
        'GL Entry',
        filters=[
            ['voucher_type', '=', 'Purchase Invoice'],
            ['project', '=', '']
        ],
        fields=['name', 'voucher_no']
    )
    cached_dict = {}
    for gl_entry in gl_entries:
        project = _get_project_from_purchase_invoice_item(cached_dict, gl_entry.get('voucher_no'))
        if project:
            frappe.db.sql("""
                UPDATE `tabGL Entry`
                SET project = %(project)s
                WHERE name = %(name)s
            """, {'name': gl_entry.get('name'), 'project': project})


def _get_project_from_purchase_invoice_item(cached, purchase_invoice):
    if purchase_invoice not in cached:
        purchase_invoice_item = frappe.db.sql("""
            SELECT project
            FROM `tabPurchase Invoice Item`
            WHERE parent=%(purchase_invoice)s
            AND project != ''
        """, {'purchase_invoice': purchase_invoice}, as_dict=1)
        cached[purchase_invoice] = purchase_invoice_item[0].get('project') if purchase_invoice_item else ''
    return cached[purchase_invoice]
