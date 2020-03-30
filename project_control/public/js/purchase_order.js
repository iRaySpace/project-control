const PurchaseOrder = erpnext.buying.PurchaseOrderController.extend({
  items_add: function(doc, cdt, cdn) {
    if (!doc.project) {
      return;
    }
    frappe.model.set_value(cdt, cdn, 'project', doc.project);
  }
});

$.extend(cur_frm.cscript, new PurchaseOrder({ frm: cur_frm }));
