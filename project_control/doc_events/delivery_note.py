import frappe
from erpnext.controllers.stock_controller import StockController


def validate(doc, method):
    StockController.check_expense_account = _overrided_check_expense_account


def _overrided_check_expense_account(self, item):
    if not item.get("expense_account"):
        frappe.throw(
            _("Expense or Difference account is mandatory for Item {0} as it impacts overall stock value").format(
                item.item_code))

    else:
        is_expense_account = frappe.db.get_value("Account",
                                                 item.get("expense_account"), "report_type") == "Profit and Loss"
        if self.doctype not in (
                "Purchase Receipt", "Purchase Invoice", "Stock Reconciliation",
                "Stock Entry", "Delivery Note") and not is_expense_account:
            frappe.throw(_("Expense / Difference account ({0}) must be a 'Profit or Loss' account")
                         .format(item.get("expense_account")))
        if is_expense_account and not item.get("cost_center"):
            frappe.throw(_("{0} {1}: Cost Center is mandatory for Item {2}").format(
                _(self.doctype), self.name, item.get("item_code")))

