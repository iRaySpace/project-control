import frappe


def execute():
    gl_entries = frappe.db.get_all(
        'GL Entry',
        filters=[
            ['voucher_type', '=', 'Delivery Note'],
            ['project', '=', '']
        ],
        fields=['name', 'voucher_no']
    )
    cached_dict = {}
    for gl_entry in gl_entries:
        project = _get_project_from_delivery_note(cached_dict, gl_entry.get('voucher_no'))
        frappe.db.sql("""
            UPDATE `tabGL Entry`
            SET project = %(project)s
            WHERE name = %(name)s
        """, {'name': gl_entry.get('name'), 'project': project})


def _get_project_from_delivery_note(cached, delivery_note):
    if delivery_note not in cached:
        cached[delivery_note] = frappe.db.get_value('Delivery Note', delivery_note, 'Project')
    return cached[delivery_note]
