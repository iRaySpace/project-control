frappe.ui.form.on('Project Budget', {
  amount: function(frm, cdt, cdn) {
    _set_budget_total(frm);
  }
});

function _set_budget_total(frm) {
  const budget_total = frm.doc.pc_budgets.reduce((total, budget) => total + budget.amount, 0.0);
  frm.set_value('pc_budget_total', budget_total);
}
