import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

@frappe.whitelist()
def after_install():
    custom_field_user()
    
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
    create_custom_field(
        "User",
        {
            "label": _("Stock Balance by Warehouse"),
            "fieldname": "stock_balance_by_warehouse",
            "fieldtype": "Check",
            "insert_after": "section_break_report_permission",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Work order with Operation"),
            "fieldname": "wo_with_operation",
            "fieldtype": "Check",
            "insert_after": "stock_balance_by_warehouse",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Delivery Schedule Report"),
            "fieldname": "delivery_schedule_report",
            "fieldtype": "Check",
            "insert_after": "wo_with_operation",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Purchase Order Pending Received Qty"),
            "fieldname": "po_pending_rec_qty",
            "fieldtype": "Check",
            "insert_after": "delivery_schedule_report",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Item Report"),
            "fieldname": "item_report",
            "fieldtype": "Check",
            "insert_after": "po_pending_rec_qty",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Sales Order Report By Customer"),
            "fieldname": "so_report_by_customer",
            "fieldtype": "Check",
            "insert_after": "item_report",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("End to End Tracebility Report"),
            "fieldname": "end_tracebility_report",
            "fieldtype": "Check",
            "insert_after": "so_report_by_customer",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Jobwork Detailed Report"),
            "fieldname": "jobwork_detailed_report",
            "fieldtype": "Check",
            "insert_after": "end_tracebility_report",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Work Order Summary Report"),
            "fieldname": "workorder_summary_report",
            "fieldtype": "Check",
            "insert_after": "jobwork_detailed_report",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Machine Availability Report"),
            "fieldname": "machine_availability_report",
            "fieldtype": "Check",
            "insert_after": "workorder_summary_report",
        },
    )



    create_custom_field(
        "User",
        {
            "label": _("Midocean User"),
            "fieldname": "midocean_user",
            "fieldtype": "Check",
            "insert_after": "enabled",
        },
    )

    create_custom_field(
        "User",
        {
            "label": _("User Permission"),
            "fieldname": "user_permission",
            "fieldtype": "Link",
            "options": "Role Profile",
            "insert_after": "username",
        },
    )

    # create_custom_field(
    #     "User",
    #     {
    #         "label":_("Allow Modules"),
    #         "fieldname": "allow_modules",
    #         "fieldtype": "Link",
    #         "options": "Module Profile",
    #         "insert_after": "user_permission",
    #     },
    # )

    create_custom_field(
        "User",
        {
            "label": _("Active Mobile App"),
            "fieldname": "active_mobile_app",
            "fieldtype": "Check",
            "insert_after": "user_fcm_token",
        },
    )

    create_custom_field(
        "User",
        {
            "label": _("User FCM Token"),
            "fieldname": "user_fcm_token",
            "fieldtype": "Small Text ",
            "insert_after": "time_zone",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("CRM"),
            "fieldname": "crm",
            "fieldtype": "Check",
            "insert_after": "customer_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("RM Transfer"),
            "fieldname": "rm_transfer",
            "fieldtype": "Check",
            "insert_after": "pr_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Internal Transfer"),
            "fieldname": "internal_transfer",
            "fieldtype": "Check",
            "insert_after": "rm_transfer",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Check",
            "insert_after": "crm",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Jobwork Module"),
            "fieldname": "jobwork_module",
            "fieldtype": "Check",
            "insert_after": "dn_check",
        },
    )

    create_custom_field(
        "User",
        {
            "label": _("Mobile Application Access"),
            "fieldname": "app_access",
            "fieldtype": "Section Break",
            "insert_after": "api_secret",
        },
    )

    create_custom_field(
        "User",
        {
            "label": _("Lead"),
            "fieldname": "lead_check",
            "fieldtype": "Check",
            "insert_after": "app_access",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Opportunity"),
            "fieldname": "opportunity_check",
            "fieldtype": "Check",
            "insert_after": "lead_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Quotation"),
            "fieldname": "quotation_check",
            "fieldtype": "Check",
            "insert_after": "opportunity_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Customer"),
            "fieldname": "customer_check",
            "fieldtype": "Check",
            "insert_after": "quotation_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _(""),
            "fieldname": "column_break_check",
            "fieldtype": "Column Break",
            "insert_after": "customer_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Sales Order"),
            "fieldname": "so_check",
            "fieldtype": "Check",
            "insert_after": "column_break_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Work Order"),
            "fieldname": "wo_check",
            "fieldtype": "Check",
            "insert_after": "so_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Purchase Order"),
            "fieldname": "po_check",
            "fieldtype": "Check",
            "insert_after": "wo_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Purchase Receipt"),
            "fieldname": "pr_check",
            "fieldtype": "Check",
            "insert_after": "po_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _(""),
            "fieldname": "column_break_check1",
            "fieldtype": "Column Break",
            "insert_after": "pr_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("BOM"),
            "fieldname": "bom_check",
            "fieldtype": "Check",
            "insert_after": "column_break_check1",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Job Card"),
            "fieldname": "jc_check",
            "fieldtype": "Check",
            "insert_after": "bom_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Stock Entry"),
            "fieldname": "se_check",
            "fieldtype": "Check",
            "insert_after": "jc_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Delivery Note"),
            "fieldname": "dn_check",
            "fieldtype": "Check",
            "insert_after": "se_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _(""),
            "fieldname": "column_break_check21",
            "fieldtype": "Column Break",
            "insert_after": "dn_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Jobwork Out"),
            "fieldname": "jwout_check",
            "fieldtype": "Check",
            "insert_after": "column_break_check21",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Jobwork In"),
            "fieldname": "jwin_check",
            "fieldtype": "Check",
            "insert_after": "jwout_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Item"),
            "fieldname": "item_check",
            "fieldtype": "Check",
            "insert_after": "jwin_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Machine with Production"),
            "fieldname": "machine_with_production",
            "fieldtype": "Check",
            "insert_after": "item_check",
        },
    )
    create_custom_field(
        "User",
        {
            "label": _("Daily Production Plan"),
            "fieldname": "daily_production_plan",
            "fieldtype": "Check",
            "insert_after": "machine_with_production",
        },
    )
