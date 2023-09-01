import json
import os
import calendar
import frappe
from frappe import _
from frappe.auth import LoginManager
from mtpl_api.mobile_api.v100.api_utils import gen_response, exception_handler, generate_key, mtpl_validate


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        validate_employee(login_manager.user)
        login_manager.post_login()
        if frappe.response["message"] == "Logged In":
            frappe.response["user"] = login_manager.user
            frappe.response["key_details"] = generate_key(login_manager.user)
        gen_response(200, frappe.response["message"])
    except frappe.AuthenticationError:
        gen_response(500, frappe.response["message"])
    except Exception as e:
        return exception_handler(e)

def validate_employee(user):
    if not frappe.db.exists("Employee", dict(user_id=user)):
        frappe.response["message"] = "Please link Employee with this user"
        raise frappe.AuthenticationError(frappe.response["message"])
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_order_list():
    try:
        if not status_field:
            status_field = "status"
        order_list = frappe.get_list(
            "Sales Order",
            fields=[
                "name",
                "customer_name",
                "DATE_FORMAT(transaction_date, '%d-%m-%Y') as transaction_date",
                "grand_total",
                f"{status_field} as status",
                "total_qty",
            ],
        )
        gen_response(200, "Order list get successfully", order_list)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for sales order")
    except Exception as e:
        return exception_handler(e)