import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    create_custom_fields(CREATE_FIELDS, ignore_validate=True)

CREATE_FIELDS = {
    "Journal Entry": [
        {
            "label": "ORC",
            "fieldname": "custom_orc",
            "fieldtype": "Check",
            "insert_after": "voucher_type",
            "is_system_generated": 0
        },
        {
            "label": "Project",
            "fieldname": "project",
            "fieldtype": "Link",
            "insert_after": "company",
            "options": "Project",
            "is_system_generated": 0
        }
    ]
}