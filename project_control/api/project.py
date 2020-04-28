import frappe


@frappe.whitelist()
def get_journal_costs(project):
    journal_costs = 0.0
    journal_entry = frappe.db.sql("""
        SELECT 
            SUM(debit_in_account_currency) as total_debit,
            SUM(credit_in_account_currency) as total_credit
        FROM `tabJournal Entry Account`
        WHERE docstatus=1
        AND project=%s
    """, project, as_dict=1)
    if journal_entry:
        total_debit = journal_entry[0].get('total_debit') or 0.0
        total_credit = journal_entry[0].get('total_credit') or 0.0
        journal_costs = total_debit - total_credit
    return journal_costs


@frappe.whitelist()
def get_delivery_note_costs(project):
    delivery_note_costs = 0.0
    delivery_note = frappe.db.sql("""
        SELECT SUM(grand_total) as costs
        FROM `tabDelivery Note`
        WHERE docstatus=1
        AND project=%s 
    """, project, as_dict=1)
    if delivery_note:
        delivery_note_costs = delivery_note[0].get('costs') or 0
    return delivery_note_costs
