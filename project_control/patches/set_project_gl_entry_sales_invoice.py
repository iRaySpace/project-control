import frappe


def execute():
    gl_entries = frappe.db.get_all(
        'GL Entry',
        filters=[
            ['voucher_type', '=', 'Sales Invoice'],
            ['project', '=', '']
        ],
        fields=['name', 'voucher_no']
    )
    cached_dict = {}
    for gl_entry in gl_entries:
        project = _get_project_from_sales_invoice(cached_dict, sales_invoice=gl_entry.get('voucher_no'))
        frappe.db.sql("""
            UPDATE `tabGL Entry`
            SET project = %(project)s
            WHERE name = %(name)s
        """, {'name': gl_entry.get('name'), 'project': project})


def _get_project_from_sales_invoice(cached, sales_invoice):
    if sales_invoice not in cached:
        cached[sales_invoice] = frappe.db.get_value('Sales Invoice', sales_invoice, 'Project')
    return cached[sales_invoice]
