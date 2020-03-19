from project_control.data import validate_project_costing


def validate(order, method):
    for item in order.items:
        if item.project:
            validate_project_costing(item.project, item.amount)
