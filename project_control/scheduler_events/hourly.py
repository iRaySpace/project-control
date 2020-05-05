import math
import frappe
from frappe.utils.data import getdate, nowdate


def set_estimated_gross_margin():
    projects = frappe.get_all('Project')
    for project in projects:
        project_name = project.get('name')
        data = frappe.db.sql("""
            SELECT 
                pc_estimated_total,
                total_sales_amount
            FROM `tabProject`
            WHERE name=%s
        """, project_name, as_dict=True)
        if data:
            project = data[0]
            estimated_gross_margin = project['total_sales_amount'] - project['pc_estimated_total']
            frappe.db.set_value('Project', project_name, 'pc_estimated_gross_margin', estimated_gross_margin)


# project_control.scheduler_events.hourly.set_gross_gratuity
def set_gross_gratuity():
    employees = frappe.db.sql("""
        SELECT 
            name, 
            employee_name,
            date_of_joining, 
            nationality,
            pc_gratuity_paid_till_date
        FROM `tabEmployee`
        WHERE status = 'Active'
    """, as_dict=1)

    filtered_employees = list(filter(lambda x: x['nationality'] != 'Bahraini', employees))
    salaries = _get_salaries()

    now = nowdate()

    for employee in filtered_employees:
        name = employee.get('name')
        date_of_joining = employee.get('date_of_joining')
        working_years, last_working_year_days = _year_diff(now, date_of_joining)

        salary = salaries.get(name, 0.00)
        total_gratuity = sum([
            _get_gross_gratuity(working_years, salary),
            _get_per_day_gratuity(working_years, last_working_year_days, salary),
            -employee.get('pc_gratuity_paid_till_date', 0)
        ])

        frappe.db.set_value('Employee', name, 'pc_gratuity_till_date', total_gratuity)


def _get_salaries():
    gratuity_base_on = frappe.db.get_single_value('Ashbee Settings', 'gratuity_base_on')

    salary_columns = ['base']
    if gratuity_base_on == 'Gross':
        salary_columns.append('variable')

    salary_select = " + ".join(salary_columns)

    salaries = frappe.db.sql("""
        SELECT
            {} AS salary,
            employee
        FROM `tabSalary Structure Assignment`
        WHERE docstatus = 1
    """.format(salary_select), as_dict=1)

    return {salary['employee']: salary['salary'] for salary in salaries}


def _year_diff(string_ed_date, string_st_date):
    days_diff = (getdate(string_ed_date) - getdate(string_st_date)).days
    return math.floor(days_diff / 365.0), days_diff % 365


def _get_gross_gratuity(working_years, gross_salary):
    """
    Calculates yearly gratuity and summed gratuity
    :param working_years:
    :param gross_salary:
    :return:
    """
    gratuities = []
    for nth_year in range(1, working_years + 1):
        gratuity_days = 30.0 if nth_year > 3 else 15.0
        gratuity = _calculate_gratuity(1, DAYS_PER_YEAR, gratuity_days, gross_salary)
        gratuities.append(gratuity)

    return sum(gratuities)


def _get_per_day_gratuity(working_years, last_working_days, gross_salary):
    """
    Calculates gratuity for the year
    :param working_years:
    :param gross_salary:
    :return:
    """
    last_working_year = last_working_days / DAYS_PER_YEAR

    if working_years > 3:
        gratuity = gross_salary * last_working_year
    else:
        gratuity = (gross_salary / 2) * last_working_year

    return gratuity


def _calculate_gratuity(no_of_years, days_per_year, gratuity_days, gross_salary):
    """
    Indemnity calculation
    Source: https://github.com/hafeesk/Hr/blob/master/hr_bahrain/hr_bahrain/hr_controllers.py
    :param no_of_years:
    :param days_per_year:
    :param gratuity_days:
    :param gross_salary:
    :return:
    """
    total_no_of_months = no_of_years * 12
    # total_no_of_months = 168

    total_no_of_days_gratuity = no_of_years * days_per_year
    # total_no_of_days_gratuity = 4936

    total_no_of_days_for_gratuity = no_of_years * gratuity_days
    # total_no_of_days_for_gratuity =====> 11 years = 330, 3 years = 45 ===> 375

    days_per_month_gratuity = total_no_of_days_for_gratuity / total_no_of_months
    # days_per_month_gratuity = 2.2321425

    gratuity_per_working_day = days_per_month_gratuity / 30
    #  gratuity_per_working_day = 0.07440475

    gratuity_for_total_working_days = gratuity_per_working_day * total_no_of_days_gratuity
    # gratuity_for_total_working_days = 367.261846

    basic_salary = gross_salary * 12
    # basic_salary = 5400

    per_day_basic_salary = basic_salary / 365
    # per_day_basic_salary = 14.79

    amount_of_gratuity = (per_day_basic_salary * gratuity_for_total_working_days) or 0
    # amount_of_gratuity = 5431.8027
    return amount_of_gratuity
