import frappe


def execute():
    frappe.db.sql("""
        UPDATE `tabDocType`
        SET autoname = 'naming_series:'
        WHERE name = 'Project'
    """)
