from functools import reduce


def validate(project, method):
    _set_budget_total(project)
    _set_variation_total(project)
    _set_estimated_total(project)


def _set_budget_total(project):
    budget_total = reduce(lambda total, budget: total + budget.amount, project.pc_budgets, 0.0)
    project.pc_budget_total = budget_total


def _set_variation_total(project):
    variation_total = reduce(lambda total, budget: total + budget.amount, project.pc_variations, 0.0)
    project.pc_variation_total = variation_total


def _set_estimated_total(project):
    project.pc_estimated_total = sum([project.pc_budget_total, project.pc_variation_total])
