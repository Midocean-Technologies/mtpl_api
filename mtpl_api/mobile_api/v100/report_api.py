import frappe
from frappe.utils import flt
from erpnext.stock.doctype.batch.batch import get_batch_qty
from datetime import datetime
# from brass_industries.api import get_traceability_report
from datetime import datetime, timedelta
from mtpl_api.mobile_api.v100.api_utils import gen_response, exception_handler, generate_key, mtpl_validate



#===================  Work order Summary report========================

@frappe.whitelist(allow_guest=True)
def workorder_summary_report(item=None, work_order=None,operation=None):
    
    where_clause = ''
    if item:
        where_clause += " and wo.production_item = '{}' ".format(item)

    if work_order:
        where_clause += " and wo.name = '{}' ".format(work_order)
    
    if operation:
        where_clause += " and op.operation = '{}' ".format(operation)

    query = """
            SELECT
                wo.name AS work_order_name,
                op.operation,
                wo.qty,
                op.completed_qty,
                wo.production_item,
                wo.stock_uom,
                op.workstation
            FROM
                `tabWork Order` wo
            INNER JOIN
                `tabWork Order Operation` op ON op.parent = wo.name
            WHERE 1=1 {} AND wo.docstatus = '1'
            order by wo.name, op.operation
        """.format(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
        <body>
            <div class="section-6">
            <table class="table table-bordered" style="font-size:20px; margin-bottom:18px;">
                <tr style="background-color: #adcfee">
                    <td style="font-weight: bold;">Work Order</td>
                    <td style="font-weight: bold;">Operation</td>
                    <td style="font-weight: bold;">Machine</td>
                    <td style="font-weight: bold;">Total Qty</td>
                    <td style="font-weight: bold;">Completed Qty</td>
                    <td style="font-weight: bold;">Pending Qty</td>
                </tr>"""
                
        
    for i in data:        
        html += """
                    <tr>
                        <td>{} &nbsp;[<b>{}</b>] </td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{} &nbsp;({})</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                """.format(i[0],i[4], i[1],i[6], i[2],i[5], i[3], i[2]-i[3])
    
    html += """
            </table>
            </div>
        </body>
    """

    return html


#===================Machine Availability Report========================

@frappe.whitelist()
def machine_availability_report(machine=None):
    where_clause = ''
    
    if machine:
        where_clause += " and t.workstation = '{}' ".format(machine)

    query = """
            SELECT t.workstation,t.start_date,t.end_date FROM `tabMachine Data` t WHERE 1=1 {}
            order by t.workstation
        """.format(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
        <body>
            <div class="section-6">
            <table class="table table-bordered" style="font-size:20px; margin-bottom:15px;">
                <tr style="background-color: #adcfee">
                    <td style="font-weight: bold;">Machine Name</td>
                    <td style="font-weight: bold;">Occupied Date</td>
                    <td style="font-weight: bold;">Available On</td>
                    <td style="font-weight: bold;">Current Status</td>
                </tr>"""

    for i in data:
        start_date = i[1].date()
        end_date= i[2].date()
        
        available_on = end_date + timedelta(days=1)
        available_on_formatted = available_on.strftime("%d-%m-%Y")
        start_date_formatted = start_date.strftime("%d-%m-%Y")
        end_date_formatted = end_date.strftime("%d-%m-%Y")
        current_date = datetime.today().date()
        current_date_formatted = current_date.strftime("%d-%m-%Y")
        #(current_date_formatted)

        
        if start_date <= current_date <= end_date:
            status = "Occupied"
        else:
            status = "Available"

        
        html += """
                    <tr>
                        <td>{}</td>
                        <td>{}&nbsp;-&nbsp;{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                """.format(i[0], start_date_formatted, end_date_formatted, available_on_formatted,status)
    
    html += """
            </table>
            </div>
        </body>
    """

    return html


#========================= STOCK BALANCE BY WAREHOUSE ====================

@frappe.whitelist()
def stock_balance_by_warehouse(item=None, warehouse=None):
    where_clause = ''
    if item:
        where_clause += " and ti.name = '%s' " % (item)

    if warehouse:
        where_clause += " and tw.name = '%s' " % (warehouse)

    query = """
            SELECT 
                ti.name, 
                tw.name,
                ti.stock_uom
            FROM tabItem ti, tabWarehouse tw 
            WHERE ti.is_stock_item = '1'
            %s
        """%(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
    <body>
        <div class="section-6">
        <table class="table table-bordered" style="font-size:15px; margin-bottom:15px;">
            <tr style="background-color: #adcfee">
                <td style="font-weight: bold;">Item</td>
                <td style="font-weight: bold;">Warehouse</td>
                <td style="font-weight: bold;">UOM</td>
                <td style="font-weight: bold;">Current Balance</td>
            </tr>"""
    
    item_list = []
    for item in data:
        item_list.append(str(item[0]))
    used_item_list = []
    for i in data:
        current_qty = get_batch_qty(item_code=i[0], warehouse=i[1])
        if current_qty:
            qty = current_qty[0]['qty']
        else:
            qty = 0.00
        
        no_of_item = item_list.count(str(i[0]))
        if str(i[0]) not in used_item_list:
            html += """<tr>"""
            html += """<td rowspan=%s>%s</td>"""%(no_of_item, str(i[0]))
            used_item_list.append(str(i[0]))

        html +="""
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            """%(i[1], i[2], str(round(flt(qty),2)))
    html += """
    </table>
    </div>
    </body>
        """
    return html

#========================= WORK ORDER WITH OPERATION  ====================

@frappe.whitelist(allow_guest=True)
def work_order_with_operations(item=None, work_order=None):
    where_clause = ''
    if item:
        where_clause += " and two.production_item = '%s' " % item

    if work_order:
        where_clause += " and twoo.parent = '%s' " % work_order

    query = """
        SELECT 
            twoo.parent,
            two.name,
            (SELECT two.production_item FROM `tabWork Order` two WHERE two.name = twoo.parent) as Production_Item,
            two.qty,
            twoo.operation,
            twoo.workstation,
            twoo.completed_qty,
            two.qty - twoo.completed_qty as Pending_Qty,
            two.stock_uom
            
        FROM `tabWork Order Operation` twoo
        INNER JOIN `tabWork Order` two ON two.name = twoo.parent
        WHERE 1 = 1
        %s
        ORDER BY twoo.parent DESC 
    """ % where_clause

    data = frappe.db.sql(query, as_list=1)
    html = """
        <style>
            h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
        </style>
    """

    work_order_list = []
    for ii in data:
        work_order_qty = frappe.get_value("Work Order", ii[0], "qty")
        if work_order_qty is not None:
            if ii[0] + " | " + ii[2] + " | " + str(work_order_qty) not in work_order_list:
                work_order_list.append(ii[0] + " | " + ii[2] + " | " + str(work_order_qty))

    for k in work_order_list:
        html += """
            <body>
                <section class="section-6">
                    <details>
                        <summary style="font-size:15px;">%s</summary>
                        <table class="table table-bordered" style="font-size:15px; margin-bottom:15px;">
                            <thead>
                                <tr style="background-color: #2b357f; color:white;">
                                    <th scope="col">Work Order</th>
                                    <th scope="col">Operation</th>
                                    <th scope="col">WorkStation</th>
                                    <th scope="col">Qty</th>
                                    <th scope="col">Completed Qty</th>
                                    <th scope="col">Pending Qty</th>
                                </tr>
                            </thead>
                            <tbody>
        """ % k

        for kk in data:
            split_data = k.split("|")
            if kk[0] == split_data[0][0:-1]:
                html += """
                    <tr style="background-color: white; color:black;">
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s &nbsp;(%s)</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                """ % (
                    str(kk[1]),
                    str(kk[4]),
                    str(kk[5]),
                    str(kk[3]),str(kk[8]),
                    str(kk[6]),
                    str(kk[7]),
                )

        html += """
                            </tbody>
                        </table>
                        <hr>
                    </details>
                </section>
            </body>
        """

    return html

#========================= Delivery Schedule Report ====================

@frappe.whitelist()
def delivery_schedule_report(sales_order=None, customer=None, item=None, delivery_date=None):
    where_clause = ''
    if item:
        where_clause += " and tsoi.item_code = '%s' " % (item)

    if sales_order:
        where_clause += " and tsoi.parent = '%s' " % (sales_order)
    
    if customer:
        where_clause += " and tso.customer = '%s' " % (customer)

    if delivery_date:
        date = datetime.strptime(delivery_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        where_clause += " and tsoi.delivery_date = '%s' " % (date)

    query = """
           SELECT 
                tsoi.parent,
                tso.customer,
                tso.transaction_date,
                tsoi.item_code,
                tsoi.delivery_date,
                tsoi.qty,
                tsoi.uom,
                tsoi.delivered_qty
            FROM `tabSales Order Item` tsoi
            LEFT JOIN `tabSales Order` tso 
            ON tso.name = tsoi.parent 
            WHERE 1 = 1
            AND tsoi.delivered_qty != tsoi.qty
            %s
            ORDER by tsoi.parent DESC
        """%(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
    <body>
        <div class="section-6">
        <table class="table table-bordered" style="font-size:16px; margin-bottom:15px;" width=100%>
            <tr style="background-color: #adcfee">
                <td style="font-weight: bold;">Sales Order</td>
                <td style="font-weight: bold; width:20%" >Customer</td>
                <td style="font-weight: bold;">Sales Order Date</td>
                <td style="font-weight: bold;">Item</td>
                <td style="font-weight: bold;">Delivery Date</td>
                <td style="font-weight: bold;">Qty</td>
                <td style="font-weight: bold;">UOM</td>
                <td style="font-weight: bold; width:5%">Delivered Qty</td>
                <td style="font-weight: bold; width:10%">Pending Delivered Qty</td>
            </tr>"""
    
    so_list = []
    for so in data:
        so_list.append(str(so[0]))
    used_so_list = []
    for i in data:
        no_of_so = so_list.count(str(i[0]))
        #(no_of_so)
        if str(i[0]) not in used_so_list:
            html += """<tr>"""
            html += """<td rowspan=%s>%s</td>"""%(no_of_so, str(i[0]))
            used_so_list.append(str(i[0]))

        html +="""
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            """%(i[1], i[2], i[3], i[4], str(round(flt(i[5]),2)), i[6], str(round(flt(i[7]),2)), str(round(flt(i[5]),2) - round(flt(i[7]),2)))
    html += """
    </table>
    </div>
    </body>
        """
    return html

#========================= Purchase Order Pending Received Qty Report ====================

@frappe.whitelist()
def purchase_order_pending_received_qty(purchase_order=None, supplier=None, item=None, required_date=None):
    where_clause = ''
    if item:
        where_clause += " and tpoi.item_code = '%s' " % (item)

    if purchase_order:
        where_clause += " and tpoi.parent = '%s' " % (purchase_order)
    
    if supplier:
        where_clause += " and tpo.supplier = '%s' " % (supplier)

    if required_date:
        date = datetime.strptime(required_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        where_clause += " and tpoi.schedule_date = '%s' " % (date)

    query = """
           SELECT 
            tpo.name,
            tpo.supplier,
            tpo.transaction_date,
            tpoi.item_code,
            tpoi.schedule_date,
            tpoi.qty,
            tpoi.uom,
            tpoi.received_qty
            FROM  
            `tabPurchase Order Item` tpoi 
            Left Join `tabPurchase Order` tpo 
            on tpo.name = tpoi.parent
            WHERE tpo.docstatus = '1'
            AND tpoi.received_qty != tpoi.qty
            %s
            ORDER BY tpo.name DESC

        """%(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
    <body>
        <div class="section-6">
        <table class="table table-bordered" style="font-size:15px; margin-bottom:15px;">
            <tr style="background-color: #adcfee">
                <td style="font-weight: bold;">Purchase Order</td>
                <td style="font-weight: bold;">Supplier</td>
                <td style="font-weight: bold;">Purchase Order Date</td>
                <td style="font-weight: bold;">Item</td>
                <td style="font-weight: bold;">Required Date</td>
                <td style="font-weight: bold;">Qty</td>
                <td style="font-weight: bold;">UOM</td>
                <td style="font-weight: bold;">Received Qty</td>
                <td style="font-weight: bold;">Pending Received Qty</td>
            </tr>"""
    
    po_list = []
    for po in data:
        po_list.append(str(po[0]))
    used_po_list = []
    for i in data:
        no_of_so = po_list.count(str(i[0]))
        if str(i[0]) not in used_po_list:
            html += """<tr>"""
            html += """<td rowspan=%s>%s</td>"""%(no_of_so, str(i[0]))
            used_po_list.append(str(i[0]))

        html +="""
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            """%(i[1], i[2], i[3], i[4], str(round(flt(i[5]),2)), i[6], str(round(flt(i[7]),2)), str(round(flt(i[5]),2) - round(flt(i[7]),2)))
    html += """
    </table>
    </div>
    </body>
        """
    return html


# =============================Sales Order Report====================
@frappe.whitelist()
def sales_order_report(customer=None, item=None):
    where_clause = ''
    
    if customer:
        where_clause += " and tso.customer = '%s' " % (customer)
    
    if item:
        where_clause += " and tsoi.item_code = '%s' " % (item)
    

    query = """
           SELECT 
                tsoi.parent,
                tso.customer,
                tsoi.item_code,
                tsoi.qty,
                tsoi.uom,
                tsoi.rate,
                tsoi.amount
            FROM `tabSales Order Item` tsoi
            LEFT JOIN `tabSales Order` tso 
            ON tso.name = tsoi.parent 
            WHERE 1 = 1
            AND tsoi.delivered_qty != tsoi.qty
            %s
            ORDER by tsoi.parent DESC
        """%(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
    <body>
        <div class="section-6">
        <table class="table table-bordered" style="font-size:18px; margin-bottom:15px;" width=100%>
            <tr style="background-color: #adcfee">
                <td style="font-weight: bold;" width=25%>Customer</td>
                <td style="font-weight: bold;" width=15%>Sales Order</td>
                <td style="font-weight: bold;" width=20%>Item</td>
                <td style="font-weight: bold;">Qty</td>
                <td style="font-weight: bold;">UOM</td>
                <td style="font-weight: bold;">Rate</td>
                <td style="font-weight: bold;">Amount</td>
            </tr>"""
    
   
    customer = []
    for i in data:
        customer.append(i[1])
    cus = list(set(customer))
    

    so_list = []
    for so in data:
        so_list.append(str(so[1]))
    used_so_list = []
    total_amount = 0

   
    customer_amounts = {}
    for x in data:
        customer = x[1]
        amount = x[6]

        if customer in customer_amounts:
            customer_amounts[customer] += amount
        else:
            customer_amounts[customer] = amount

    # #(customer_amounts)

    for x in cus:
        sum=0

                
        for i in data:
            if x == i[1]:
                no_of_so = so_list.count(str(i[1]))
                if str(i[1]) not in used_so_list:
                    html += """<tr>"""
                    html += """<td rowspan=%s>%s</td>"""%(no_of_so, str(i[1]))
                    used_so_list.append(str(i[1]))

                html +="""
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>₹ %s</td>
                            <td>₹ %s</td>
                        </tr>
                    """%(str(i[0]), str(i[2]), str(i[3]), str(i[4]),round(i[5]), round(i[6]))
                sum += i[6]
           
        html += """<tr><td colspan="6">Total Amount</td><td>₹ %s</td></tr>""" % (round(sum))
    html += """
    </table>
    </div>
    </body>
        """
    return html

# =============================Item Report====================
@frappe.whitelist()
def item_report(item=None):
    where_clause = ''
    
    if item:
        where_clause += " and tsoi.item_code = '%s' " % (item)
    

    query = """

           SELECT tsoi.item_code, tsoi.item_name, tsoi.stock_uom, tsoi.valuation_rate,
           IFNULL(so.total_quantity, 0) AS sales_order_quantity,
           IFNULL(po.total_quantity, 0) AS purchase_order_quantity
           FROM tabItem tsoi
            
            LEFT JOIN (
                SELECT item_code, SUM(qty) AS total_quantity
                FROM `tabSales Order Item`
                GROUP BY item_code
            ) so ON tsoi.item_code = so.item_code
            LEFT JOIN (
                SELECT item_code, SUM(qty) AS total_quantity
                FROM `tabPurchase Order Item`
                GROUP BY item_code
            ) po ON tsoi.item_code = po.item_code
            WHERE 1 = 1
            %s
        """%(where_clause)

    data = frappe.db.sql(query, as_list=1)
    html = """ <style>
                h1,h2,h3,h4,h5,p{
                    margin: 0 !important;
                }
                .section-6{
                    padding: 1rem;
                }
                details {
                    border: 1px solid #d4d4d4;    
                    padding: .75em .75em 0;
                    margin-top: 10px;
                    box-shadow:0 0 20px #d4d4d4;
                }
                
                summary {	
                    font-weight: bold;
                    margin: -.75em -.75em 0;
                    padding: .75em;
                    background-color: #5f75a4;
                    color: #fff;
                }
                
                details[open] {
                    padding: .75em;
                    border-bottom: 1px solid #d4d4d4;
                }
                
                details[open] summary {
                    border-bottom: 1px solid #d4d4d4;
                    margin-bottom: 10px;
                }

                .table{
                    margin: 0 !important;
                    width: 100%;
                }
                .table th, .table td{
                    padding: 0.3rem;
                }
                .table thead th{
                    border-bottom: 2px solid #46494d;
                }
                .table-bordered {
                    border: 1px solid #1b1c1e;
                }
                .table-bordered th, .table-bordered td{
                    border: 1px solid #7c7f86;
                }
            </style>"""
    html += """
    <body>
        <div class="section-6">
        <table class="table table-bordered" style="font-size:15px; margin-bottom:15px;">
            <tr style="background-color: #00bfff">
                <td style="font-weight: bold;">Item Name</td>
                <td style="font-weight: bold;">Item Code</td>
                <td style="font-weight: bold;">UOM</td>
                <td style="font-weight: bold;">Valuation Rate</td>

                <td style="font-weight: bold;">Total sale Qty</td>
                <td style="font-weight: bold;">Total Purchase Qty</td>

            </tr>"""
    

    so_list = []
    for so in data:
        so_list.append(str(so[1]))
    used_so_list = []

   
    for i in data:
        no_of_so = so_list.count(str(i[1]))
        if str(i[1]) not in used_so_list:
            html += """<tr>"""
            html += """<td rowspan=%s>%s</td>"""%(no_of_so, str(i[1]))
            used_so_list.append(str(i[1]))

        html +="""
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
            """%(str(i[0]), str(i[2]), "{:,.0f}".format(i[3]), "{:,.0f}".format(i[4]), "{:,.0f}".format(i[5]))
    html += """
    </table>
    </div>
    </body>
        """
    return html


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def delivery_schedule(sales_order=None, customer=None, item=None, delivery_date=None):
    try:
        x = delivery_schedule_report(sales_order=sales_order, customer=customer, item=item, delivery_date=delivery_date)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)



@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def wo_operations(item=None, work_order=None):
    try:
        x = work_order_with_operations(item=item, work_order=work_order)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
        

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def itemreport(item=None):
    try:
        x = item_report(item=item)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def po_pending_qty(purchase_order=None, supplier=None, item=None, required_date=None):
    try:
        x = purchase_order_pending_received_qty(purchase_order=purchase_order, supplier=supplier, item=item, required_date=required_date)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)


@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def so_report_by_customer(customer=None, item=None):
    try:
        x = sales_order_report(customer=customer, item=item)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)

# @frappe.whitelist(allow_guest=True)
# def get_tracebility(sales_order=None, work_order=None, batch=None, delivery_note=None):
#     try:
#         x = get_traceability_report(sales_order=sales_order, work_order=work_order, batch=batch, delivery_note=delivery_note)
#         return x
#     except Exception as e:
#         raise e 
        

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def wo_summary_report(item=None, work_order=None,operation=None):
    try:
        x = workorder_summary_report(item=item, work_order=work_order,operation=operation)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)        

    
@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def machine_availability(machine=None):
    try:
        x = machine_availability_report(machine=machine)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)
        

@frappe.whitelist()
@mtpl_validate(methods=["GET"])
def stock_balance_warehouse(item=None, warehouse=None):
    try:
        x = stock_balance_by_warehouse(item=item, warehouse=warehouse)
        gen_response(200, x)
    except frappe.PermissionError:
        return gen_response(500, "Not permitted")
    except Exception as e:
        return exception_handler(e)