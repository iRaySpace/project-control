frappe.ui.form.on('Project', {
  refresh: function(frm) {
    _set_project_costs(frm);
    _set_read_only_budget(frm);
  }
});


function _set_read_only_budget(frm) {
  if (frm.doc.__islocal) return;
  if (!frappe.user.has_role('Projects Manager')) {
    frm.set_df_property('pc_budgets', 'read_only', 1);
  }
}


async function _set_project_costs(frm) {
  const journal_costs = await _get_journal_costs(frm.doc.name);
  const delivery_note_costs = await _get_delivery_note_costs(frm.doc.name);
  frm.set_value('pc_total_journal_entry', journal_costs);
  frm.set_value('pc_total_delivery_note', delivery_note_costs);
}


async function _get_journal_costs(project) {
  const { message: journal_costs } = await frappe.call({
    method: 'project_control.api.project.get_journal_costs',
    args: { project },
  });
  return journal_costs;
}


async function _get_delivery_note_costs(project) {
  const { message: delivery_note_costs } = await frappe.call({
    method: 'project_control.api.project.get_delivery_note_costs',
    args: { project },
  });
  return delivery_note_costs;
}


frappe.ui.form.on('Project Budget', {
  amount: function(frm, cdt, cdn) {
    _set_budget_total(frm);
  }
});

function _set_budget_total(frm) {
  const budget_total = frm.doc.pc_budgets.reduce((total, budget) => total + budget.amount, 0.0);
  frm.set_value('pc_budget_total', budget_total);
}
