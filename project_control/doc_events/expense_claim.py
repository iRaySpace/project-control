from project_control.data import validate_project_costing_for_warning


def validate(expense_claim, method):
    if hasattr(expense_claim, '__islocal'):
        if expense_claim.project:
            validate_project_costing_for_warning(expense_claim.project, expense_claim.total_sanctioned_amount)
