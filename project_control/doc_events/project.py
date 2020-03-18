from functools import reduce


def validate(project, method):
    _set_budget_total(project)


def _set_budget_total(project):
    budget_total = reduce(lambda total, budget: total + budget.amount, project.pc_budgets, 0.0)
    project.pc_budget_total = budget_total
