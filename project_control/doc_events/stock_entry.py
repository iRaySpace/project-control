from project_control.data import validate_project_costing


def validate(stock_entry, method):
    if stock_entry.project:
        validate_project_costing(stock_entry.project, stock_entry.value_difference, stock_entry.pc_stock_item_issue)
