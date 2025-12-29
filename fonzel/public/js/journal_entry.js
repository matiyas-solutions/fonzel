frappe.ui.form.on("Journal Entry", {
    company: function(frm) {
        cur_frm.set_value("project", null);
    },
    project: function(frm) {
        frm.set_query("project", function() {
            return {
                "filters": {
                    "company": frm.doc.company
                }
            };
        });
        frm.doc.accounts.forEach(function(row) {
           frappe.model.set_value(row.doctype, row.name, "project", frm.doc.project);
        });
        frm.refresh_field("accounts");
    }  
});   
frappe.ui.form.on('Journal Entry Account', {
    accounts_add: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (frm.doc.project) {
            frappe.model.set_value(row.doctype, row.name, "project", frm.doc.project);
            frm.refresh_field("accounts");
        }
    }
}); 

