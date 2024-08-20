import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

@frappe.whitelist()
def after_install():
    pass
    
def custom_field_user():
    create_custom_field(
        "User",
        {
            "label": _("Report Permission"),
            "fieldname": "section_break_report_permission",
            "fieldtype": "Section Break",
            "insert_after": "generate_keys",
        },
    )
   