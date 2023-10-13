import json
import os
import calendar
import frappe
from frappe import _
from frappe.auth import LoginManager
from frappe.model.workflow import get_transitions, get_workflow
from frappe.workflow.doctype.workflow_action.workflow_action import confirm_action, apply_action, apply_workflow, filter_allowed_users
from mtpl_api.mobile_api.v1.api_utils import gen_response, exception_handler, generate_key, mtpl_validate
from erpnext.stock.doctype.batch.batch import get_batch_qty
from frappe.utils import flt, now, now_datetime, get_first_day, get_last_day, get_year_start, get_year_ending, time_diff_in_seconds, format_date
from frappe.utils.file_manager import save_file, save_file_on_filesystem, remove_file


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        # validate_employee(login_manager.user)
        login_manager.post_login()
        if frappe.response["message"] == "Logged In":
            if not frappe.db.exists("Smart Connect User", login_manager.user):
                return gen_response(500, "User has no permission for mobile app, Please Contect Admin")
            
            if frappe.get_value("Smart Connect User", login_manager.user, "enable") == 0:
                return gen_response(500, "User has no permission for mobile app, Please Contect Admin")
            # if frappe.get_doc("Smart Connect User", login_manager.user)
            frappe.response["user"] = login_manager.user
            frappe.response["key_details"] = generate_key(login_manager.user)
            frappe.response["smart_user_details"] = frappe.get_doc('Smart Connect User', login_manager.user)
            frappe.response["user_details"] = frappe.get_doc('User', login_manager.user)
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
def update_workrecord(work_record, operation, workstation):
    try:
        doc = frappe.get_doc("Work Order", work_record)
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
def get_workorder_operation_details_list(work_order=None, operation=None, production_item=None, status=None,
                                         workstation=None):
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
                            if operation == j.operation and (
                                    not workstation or workstation == j.workstation) and j.completed_qty == 0:
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
                            if operation == j.operation and (
                                    not workstation or workstation == j.workstation) and j.completed_qty > 0 and j.completed_qty < workOrderDoc.qty:
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
                            if (
                                    not workstation or workstation == j.workstation) and j.completed_qty > 0 and j.completed_qty < workOrderDoc.qty:
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
                            if operation == j.operation and (
                                    not workstation or workstation == j.workstation) and j.completed_qty >= workOrderDoc.qty:
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
                            if (
                                    not workstation or workstation == j.workstation) and j.completed_qty >= workOrderDoc.qty:
                                temp = {}
                                temp["work_order"] = workOrderDoc.name
                                temp["operation"] = j.operation
                                temp["production_item"] = workOrderDoc.production_item
                                temp["workstation"] = j.workstation
                                temp["completed_qty"] = j.completed_qty
                                temp["bom_no"] = workOrderDoc.bom_no
                                temp["for_quantity"] = workOrderDoc.qty
                                res.append(temp)

        gen_response(200, "Work Order Operation List get Successfully", res)
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
        gen_response(200, "Work Order Raw Material Get Successfully", x)
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

        gen_response(200, "Item Data get successfully", item_list)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for Item")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def fetch_item(item):
    try:
        itemlist = frappe.get_all("Item", filters={'name': item}, fields=['*'])
        for x in itemlist:
            doc = frappe.get_doc("Item", x.name)
            bindoc = frappe.get_all("Bin", filters={'item_code': item},
                                    fields=['item_code', 'warehouse', 'actual_qty', 'stock_uom'])

            for i in bindoc:
                itemdoc = frappe.get_doc("Item", i.item_code)
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
            x['stock_levels'] = bindoc
        gen_response(200, "Item get Successfully", itemlist[0])
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
                gen_response(200, "Quality Inspection get successfully", i.quality_inspection_template)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_workorder_record_list():
    try:  
        data = frappe.get_list("Work Order",fields= ["*"])
        gen_response(200,"Data fetch successfully" ,data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for work order")
    except Exception as e:
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_workorder_record(record):
    try:
        data = frappe.get_doc("Work Order", record, fields=["*"])
        gen_response(200, "Work order get successfully", data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for work order")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def validate_item_batch(item):
    try:
        doc = frappe.get_doc("Item", item)
        gen_response(200, "Data fetch successfully", doc.has_batch_no)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for work order")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def validate_item_uom(item):
    try:
        doc = frappe.get_doc("Item", item)
        gen_response(200, "Data fetch successfully", doc.stock_uom)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted for work order")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_crm_html():
    try:
        crm_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CRM Page</title>
        </head>
        <body>
            <h1>Welcome to the CRM Module</h1>
            <p>This is a simple HTML page for the CRM module in Frappe.</p>
            
        </body>
        </html>
        """
        gen_response(200, crm_html)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def fetch_event_record(reference_docname):
    try:
        query = """SELECT * from `tabEvent Participants` tep left join tabEvent te on te.name = tep.parent WHERE tep.reference_docname = '%s'"""%(reference_docname)
        data = frappe.db.sql(query, as_dict=1)
        # doc = frappe.get_list('Event Participants', filters={"reference_docname": reference_docname}, fields=["*"])
        if not len(data):
            return gen_response(200 ,"No Data Found", data)
        gen_response(200 ,"Data Fetch Succesfully", data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def fetch_comment_record(lead_name):
    try:
        query = """SELECT * from `tabCRM Note` tcn WHERE tcn.parent = '%s'"""%(lead_name)
        data = frappe.db.sql(query, as_dict=1)
        # doc = frappe.get_list('CRM Note', filters={"parent": lead_name}, fields=["*"])
        gen_response(200 ,"Data Fetch Succesfully", data)

    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def fetch_company_record():
    try:
        doc = frappe.get_list('Company', fields=["*"])
        gen_response(200 ,"Data Fetch Succesfully", doc)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_sales_order_list():
    try:
        doc = frappe.get_list('Sales Order', fields=["*"])
        gen_response(200 ,"Data Fetch Succesfully", doc)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_purchase_order_list():
    try:
        doc = frappe.get_list('Purchase Order', fields=["*"])
        gen_response(200 ,"Data Fetch Succesfully", doc)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_document_type_list(user=None):
    try:
        doc = frappe.get_list('Workflow Action', filters={'status': 'Open'}, fields=['name', 'reference_name', 'reference_doctype'])
        gen_response(200 ,"Data Fetch Succesfully", doc)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
	
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_document_list(reference_doctype, user=None):
    try:
        lst = []
	
        document_list = frappe.get_list('Workflow Action', filters={'status': 'Open', 'reference_doctype': reference_doctype}, fields=['name', 'reference_name', 'reference_doctype'])
        for row in document_list:
            docc = {}
            if frappe.db.exists(row.reference_doctype, row.reference_name):
                doc = frappe.get_doc(row.reference_doctype, row.reference_name)
                docc['reference_doctype'] = row.reference_doctype
                docc['reference_name'] = row.reference_name
                docc['workflow_state'] = doc.workflow_state
                docc['status'] = get_status(doc.docstatus)
                lst.append(docc)
        gen_response(200 ,"Data Fetch Succesfully", lst)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_document_list_5_record(user=None):
    try:
        lst = []
	
        document_list = frappe.get_list('Workflow Action', filters={'status': 'Open'}, fields=['name', 'reference_name', 'reference_doctype'], limit_page_length=5)
        for row in document_list:
            docc = {}
            if frappe.db.exists(row.reference_doctype, row.reference_name):
                doc = frappe.get_doc(row.reference_doctype, row.reference_name)
                docc['reference_doctype'] = row.reference_doctype
                docc['reference_name'] = row.reference_name
                docc['workflow_state'] = doc.workflow_state
                docc['status'] = get_status(doc.docstatus)
                lst.append(docc)
        gen_response(200 ,"Data Fetch Succesfully", lst)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
def get_status(status):
	if status == 0:
		return 'Draft'

	if status == 1:
		return 'Submitted'
	
	if status == 2:
		return 'Cancelled'


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_doc_details(reference_doctype, reference_name):
    try:
        doc = frappe.get_doc(reference_doctype, reference_name)
        gen_response(200 ,"Data Fetch Succesfully", doc)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_workflow_action(reference_doctype, reference_name):
    try:
        doc = frappe.get_doc(reference_doctype, reference_name)
        workflow = get_workflow(doc.doctype)
        data = get_transitions(doc, workflow)
        gen_response(200 ,"Data Fetch Succesfully", data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_print_format(reference_doctype, reference_name):
    try:
        print_format = "Standard"
        data = frappe.get_print(doctype=reference_doctype, name=reference_name, print_format=print_format)
        gen_response(200 ,"Data Fetch Succesfully", data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def update_workflow(reference_doctype, reference_name, action):
    try:
        # doc = get_doc_details(reference_doctype, reference_name)
        doc = frappe.get_doc(reference_doctype, reference_name)
        apply_workflow(doc, action)
        gen_response(200 ,"Data Update Succesfully")
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def update_fcm_token(user, token):
    try:
        doc = frappe.get_doc('Smart Connect User', user)
        doc.db_set('user_fcm_token', token)
        frappe.db.commit()
        gen_response(200 ,"Data Update Succesfully")
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_related_user(reference_doctype, reference_name, action):
    try:
        doc = frappe.get_doc(reference_doctype, reference_name)
        workflow = get_workflow(reference_doctype)
        tr = get_transitions(doc, workflow)
        data = None
        t = None
        for i in tr:
            if i.get('action') == action:
                t = frappe.get_doc("Workflow Transition", i.name)

        user_lst = [
            row.name for row in frappe.get_all(
                'User', filters={'enabled': 1}, fields=['name'])
        ]
        if t:
            data = filter_allowed_users(user_lst, doc, t)
        data = []
        gen_response(200 ,"Data Fetch Succesfully", data)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def attach_file():
    try:
        x = json.loads(frappe.request.data)
        if not x["attachment_name"]:
            return gen_response(500 ,"File Name Not Found")
        fil = save_file(fname = x["attachment_name"], content=x["attachment"], dt=x["doctype"], dn=x["docname"], folder=None, decode=True, is_private=0, df='attechment')
        return gen_response(200 ,"File Uploaded Succesfully", fil)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_attachment_list(doctype=None, docname=None):
    try:
        filter = {}
        if doctype:
            filter["attached_to_doctype"] = doctype
        if docname:
            filter["attached_to_name"] = docname
        fileList = frappe.get_all("File", filters=filter, fields=["file_name","file_url"])
        gen_response(200 ,"Data Fetch Succesfully", fileList)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    
@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def delete_attachment(fid):
    try:
        remove_file(fid)
        gen_response(200 ,"File Deleted Succesfully")
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    

@frappe.whitelist()
@mtpl_validate(methods=["POST"])
def submit_production_workbook(record):
    try:
        Doc = frappe.get_doc("Production Workbook", record)
        Doc.submit()
        gen_response(200 ,"Record Submitted Succesfully")
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        print(e)
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def check_rm_transfer(record=None, work_order=None):
    try:
        if record != "null":
            x = production_workbook_rm_check(record)
        if work_order != "null":
            x = work_order_rm_check(work_order)
        gen_response(200 ,"Data Fetch Succesfully", x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

def production_workbook_rm_check(record):
    temp = {}
    pwDoc = frappe.get_doc("Production Workbook", record)
    woDoc = frappe.get_doc("Work Order", pwDoc.work_order)
    bomDoc = frappe.get_doc("BOM", woDoc.bom_no)
    if pwDoc.operation == woDoc.operations[0].operation:
        x_qty = 0
        pwList = frappe.get_list("Production Workbook", filters={"work_order":pwDoc.work_order}, fields=["qty"])
        if pwList:
            for i in pwList:
                x_qty += i.qty

        rm_qty = 0
        for j in bomDoc.items:
            rm_qty += j.qty

        qty = (x_qty * rm_qty ) / flt(bomDoc.quantity)

        for k in woDoc.required_items:
            if k.transferred_qty < qty:
                temp["status"] = 0
                temp["text"] = "Material Need to Transferred"
                return temp
            else:
                temp["status"] = 1
                temp["text"] = "Material Already Transferred"
                return temp
    else:
        temp["status"] = 1
        temp["text"] = "Material Already Transferred"
        return temp
    
def work_order_rm_check(work_order):
    temp = {}
    woDoc = frappe.get_doc("Work Order", work_order)
    temp["status"] = 1
    for k in woDoc.required_items:
        temp["text"] = "Requierd Material : {0} - Transferred Material {1}".format(round(k.required_qty,3), round(k.transferred_qty,3))
    return temp

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_data_from_barcode(data):
    try:
        res = {}
        if not data:
            res = {'status':0, 'message': 'data not found'}

        if frappe.db.exists("Item", data):
            itemDoc = frappe.get_doc("Item", data)
            res = {'item_code': itemDoc.name, 'uom': itemDoc.stock_uom}
        
        if frappe.db.exists("Batch", data):
            batchDoc = frappe.get_doc("Batch", data)
            itemDoc = frappe.get_doc("Item", batchDoc.item)
            res = {'item_code': itemDoc.name, 'uom': itemDoc.stock_uom}

        if frappe.db.exists("Serial No", data):
            srDoc = frappe.get_doc("Serial No", data)
            itemDoc = frappe.get_doc("Item", srDoc.item_code)
            res = {'item_code': itemDoc.name, 'uom': itemDoc.stock_uom}
        gen_response(200 ,"Data Fetch Succesfully", res)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def get_qc_template(item, operation):
    try:
        itemDoc = frappe.get_doc("Item", item)
        for i in itemDoc.item_qc:
            if i.operation == operation:
                gen_response(200 ,"Data Fetch Succesfully", i.quality_inspection_template)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
    