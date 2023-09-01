import json
import os
import calendar
import frappe
from frappe import _
from frappe.auth import LoginManager
from mtpl_api.mobile_api.v100.api_utils import gen_response, exception_handler, generate_key, mtpl_validate
from erpnext.stock.doctype.batch.batch import get_batch_qty
from frappe.utils import flt, now, now_datetime, get_first_day, get_last_day, get_year_start, get_year_ending, time_diff_in_seconds, format_date


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        # validate_employee(login_manager.user)
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
    

@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def update_workrecord(work_record,operation,workstation):
    try:
        doc = frappe.get_doc("Work Order",work_record)
        for i in doc.operations:
            if i.operation == operation:
                i.db_set("workstation", workstation)
        
        workstationDoc = frappe.get_doc("Workstation", workstation)
        workstationDoc.db_set("work_order", work_record)
        workstationDoc.db_set("operation", operation)
        
        gen_response(200, "Work Order Update Successfully")
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Work Order")
    except Exception as e:
        return exception_handler(e)
    
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_workorder_operation_details_list(work_order=None, operation=None, production_item=None, status=None, workstation=None):
    try:
        fltr = {}
        if work_order: 
            fltr["name"] = work_order
        
        if production_item:
            fltr['production_item'] = production_item
        
        fltr["docstatus"] = 1
        
        res = []

        workOrderAll = frappe.get_all("Work Order", filters=fltr, fields=["*"])
        if not status:
            for i in workOrderAll:
                workOrderDoc = frappe.get_doc("Work Order", i.name, fields=["*"])
                for j in workOrderDoc.operations:
                    if operation:
                        if operation == j.operation and (not workstation or workstation == j.workstation):
                            temp = {}
                            temp["work_order"] = workOrderDoc.name
                            temp["operation"] = j.operation
                            temp["production_item"] = workOrderDoc.production_item
                            temp["workstation"] = j.workstation
                            temp["completed_qty"] = j.completed_qty
                            temp["bom_no"] = workOrderDoc.bom_no
                            temp["for_quantity"] = workOrderDoc.qty
                            res.append(temp)
                    else:
                        if not workstation or workstation == j.workstation:
                            temp = {}
                            temp["work_order"] = workOrderDoc.name
                            temp["operation"] = j.operation
                            temp["production_item"] = workOrderDoc.production_item
                            temp["workstation"] = j.workstation
                            temp["completed_qty"] = j.completed_qty
                            temp["bom_no"] = workOrderDoc.bom_no
                            temp["for_quantity"] = workOrderDoc.qty
                            res.append(temp)
        else:
            if status == "Not Started":
                for i in workOrderAll:
                    workOrderDoc = frappe.get_doc("Work Order", i.name, fields=["*"])
                    for j in workOrderDoc.operations:
                        if operation:
                            if operation == j.operation and (not workstation or workstation == j.workstation) and j.completed_qty == 0:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)
                        else:
                            if (not workstation or workstation == j.workstation) and j.completed_qty == 0:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)
            elif status == "In Process":
                for i in workOrderAll:
                    workOrderDoc = frappe.get_doc("Work Order", i.name, fields=["*"])
                    for j in workOrderDoc.operations:
                        if operation:
                            if operation == j.operation and (not workstation or workstation == j.workstation) and j.completed_qty > 0 and j.completed_qty < workOrderDoc.qty:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)
                        else:
                            if (not workstation or workstation == j.workstation) and j.completed_qty > 0 and j.completed_qty < workOrderDoc.qty:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)

            elif status == "Completed":
                for i in workOrderAll:
                    workOrderDoc = frappe.get_doc("Work Order", i.name, fields=["*"])
                    for j in workOrderDoc.operations:
                        if operation:
                            if operation == j.operation and (not workstation or workstation == j.workstation) and j.completed_qty >= workOrderDoc.qty:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)
                        else:
                            if (not workstation or workstation == j.workstation) and j.completed_qty >= workOrderDoc.qty:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)

        gen_response(200,"Work Order Operation List get Successfully", res)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted ")
    except Exception as e:
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_wo_rm(work_order):
    try:
        x = []
        woDoc = frappe.get_doc("Work Order", work_order)
        for i in woDoc.required_items:
            res = {}
            res["name"] = i.item_code
            # res["item_name"] = i.item_name
            x.append(res)
        gen_response(200,"Work Order Raw Material Get Successfully", x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Work Order")
    except Exception as e:
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_item_data(name=None, warehouse=None):
    try:
        if not warehouse:
            pass

        filter = {}
        if name:
            filter["item_code"] = name
        
        if warehouse:
            s_warehouse = warehouse
        else:
            stock_setting = frappe.get_single("Stock Settings")
            if stock_setting.default_warehouse:
                s_warehouse = stock_setting.default_warehouse
            else:
                s_warehouse = None

        item_list = frappe.get_list("Item", filters=filter, fields=["*"])
        for i in item_list:
            available_qty = get_batch_qty(warehouse=s_warehouse, item_code=i.name)
            if available_qty:
                qty = available_qty[0]["qty"]
            else:
                qty = 0.00
            
            # if i.stock_uom == "Kg":
            #     i["available_qty_kg"] = str(qty) + " " + i.stock_uom

            #     if qty > 0.00 and i.one_piece_weight != 0.00 :
            #         nos_qty = qty / i.one_piece_weight
            #     else:
            #         nos_qty = 0.00
            #     i["available_qty_nos"] = str(nos_qty) + " " + "Nos"
            
            # if i.stock_uom == "Nos":
            #     i["available_qty_nos"] = str(qty) + " " + i.stock_uom

            #     if qty > 0.00 and i.one_piece_weight != 0.00 :
            #         kg_qty = qty * i.one_piece_weight
            #     else:
            #         kg_qty = 0.00
            #     i["available_qty_kg"] = str(kg_qty) + " " + "Kg"
        
        gen_response(200,"Item Data get successfully", item_list)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Item")
    except Exception as e:
        return exception_handler(e)

    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def fetch_item(item):
    try:	
        itemlist= frappe.get_all("Item",filters={'name':item},fields=['*'])
        for x in itemlist:
            doc= frappe.get_doc("Item",x.name)
            bindoc = frappe.get_all("Bin",filters={'item_code':item},fields= ['item_code','warehouse','actual_qty','stock_uom'])
            
            for i in bindoc:
                itemdoc= frappe.get_doc("Item",i.item_code)
                # if itemdoc.stock_uom == "Kg":
                #     if not itemdoc.one_piece_weight:
                #         conversion = 0.00
                #     else:
                #         conversion = flt(i.actual_qty) / flt(itemdoc.one_piece_weight)
                #     i['secondary qty']= conversion
                #     i['secondary_uom']= "Nos"

                # elif itemdoc.stock_uom == "Nos":
                #     conversion = flt(i.actual_qty) * flt(itemdoc.one_piece_weight)
                #     i['secondary qty']= conversion
                #     i['secondary_uom']= "Kg"
            x['stock_levels']= bindoc
        gen_response(200,"Item get Successfully", itemlist[0])
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for item")
    except Exception as e:
        return exception_handler(e)
    

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_qc_template(item, operation):
    try:
        itemDoc = frappe.get_doc("Item", item)
        for i in itemDoc.item_qc:
            if i.operation == operation:
                gen_response(200,"Quality Inspection get successfully", i.quality_inspection_template)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    