import frappe


def execute():
	gl_entries = frappe.db.get_all(
		'GL Entry',
		filters=[
			['voucher_type', '=', 'Stock Entry'],
		],
		fields=['name', 'voucher_no', 'debit', 'credit']
	)
	cached_dict = {}
	for gl_entry in gl_entries:
		total = _get_total_from_stock_entry(cached_dict, gl_entry.get('voucher_no'))
		if total > 0.0:
			debit = gl_entry.get('debit')
			credit = gl_entry.get('credit')
			if debit > 0:
				frappe.db.set_value('GL Entry', gl_entry.get('name'), 'debit', total)
			elif credit > 0:
				frappe.db.set_value('GL Entry', gl_entry.get('name'), 'credit', total)


def _get_total_from_stock_entry(cached, stock_entry):
	if stock_entry not in cached:
		cached[stock_entry] = frappe.db.get_value('Stock Entry', stock_entry, 'total_outgoing_value')
	return cached[stock_entry]

