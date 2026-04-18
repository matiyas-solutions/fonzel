import frappe
from frappe import _
from frappe.utils import nowdate

@frappe.whitelist()
def mark_attendance(status):
   

    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        frappe.throw(_("No employee found for the current user."))

    date = nowdate()

    existing = frappe.db.get_value("Attendance", {
        "employee": employee,
        "attendance_date": date,
        "docstatus": ["<", 2]
    }, "name")

    if existing:
        frappe.throw(_("Attendance is already marked for today."))
    else:
        doc = frappe.new_doc("Attendance")
        doc.employee = employee
        
        emp_details = frappe.db.get_value("Employee", employee, ["employee_name", "company", "department"], as_dict=True)
        if emp_details:
            doc.employee_name = emp_details.employee_name
            doc.company = emp_details.company
            doc.department = emp_details.department
            
        doc.attendance_date = date
        doc.status = status
        doc.half_day_status = None
        doc.flags.ignore_validate = True
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_links = True
        doc.flags.ignore_hooks = True
        doc.insert(ignore_permissions=True)
        doc.submit()
        
        frappe.msgprint(_("Attendance marked successfully as {0}.").format(status))
        return doc.name
