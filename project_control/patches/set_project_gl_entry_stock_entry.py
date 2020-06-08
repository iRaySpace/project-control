import frappe


def execute():
	gl_entries = frappe.db.get_all(
		'GL Entry',
		filters=[
			['voucher_type', '=', 'Stock Entry'],
			['project', '=', '']
		],
		fields=['name', 'voucher_no']
	)
	cached_dict = {}
	for gl_entry in gl_entries:
		project = _get_project_from_stock_entry(cached_dict, gl_entry.get('voucher_no'))
		frappe.db.sql("""
            UPDATE `tabGL Entry`
            SET project = %(project)s
            WHERE name = %(name)s
        """, {'name': gl_entry.get('name'), 'project': project})


def _get_project_from_stock_entry(cached, stock_entry):
	if stock_entry not in cached:
		cached[stock_entry] = frappe.db.get_value('Stock Entry', stock_entry, 'Project')
	return cached[stock_entry]
