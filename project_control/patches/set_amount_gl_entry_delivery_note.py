import frappe


def execute():
	gl_entries = frappe.db.get_all(
		'GL Entry',
		filters=[
			['voucher_type', '=', 'Delivery Note'],
		],
		fields=['name', 'voucher_no', 'debit', 'credit']
	)
	cached_dict = {}
	for gl_entry in gl_entries:
		total = _get_total_from_delivery_note(cached_dict, gl_entry.get('voucher_no'))
		debit = gl_entry.get('debit')
		credit = gl_entry.get('credit')
		if debit > 0:
			frappe.db.set_value('GL Entry', gl_entry.get('name'), 'debit', total)
		elif credit > 0:
			frappe.db.set_value('GL Entry', gl_entry.get('name'), 'credit', total)


def _get_total_from_delivery_note(cached, delivery_note):
	if delivery_note not in cached:
		cached[delivery_note] = frappe.db.get_value('Delivery Note', delivery_note, 'base_total')
	return cached[delivery_note]

