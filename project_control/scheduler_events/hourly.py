import frappe


def set_estimated_gross_margin():
    projects = frappe.get_all('Project')
    for project in projects:
        project_name = project.get('name')
        data = frappe.db.sql("""
            SELECT pc_estimated_total, total_sales_amount
            FROM `tabProject`
            WHERE name=%s
        """, project_name, as_dict=True)
        if data:
            project = data[0]
            estimated_gross_margin = project['total_sales_amount'] - project['pc_estimated_total']
            frappe.db.set_value('Project', project_name, 'pc_estimated_gross_margin', estimated_gross_margin)
