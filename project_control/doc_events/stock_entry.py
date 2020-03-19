from project_control.data import validate_project_costing


def validate(stock_entry, method):
    validate_project_costing(stock_entry.project, stock_entry.value_difference)
