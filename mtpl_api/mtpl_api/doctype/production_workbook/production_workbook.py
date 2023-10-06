# Copyright (c) 2023, Midocean Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, nowtime, flt
from frappe.model.document import Document

class ProductionWorkbook(Document):
	def validate(self):
		today_date = today()
		current_time = nowtime()
		
		
		if not self.posting_date:
			self.posting_date = today_date

		if not self.posting_time:
			self.posting_time = current_time
		
		if not self.workstation:
			woDoc = frappe.get_doc("Work Order", self.work_order)
			for i in woDoc.operations:
				if i.operation == self.operation:
					self.workstation = i.workstation

	def on_submit(self):
		if self.from_jobcard == 0:
			wip_warehouse = frappe.get_value("Work Order", self.work_order, "wip_warehouse")
			work_order_doc = frappe.get_doc("Work Order", self.work_order)
			production_item = frappe.get_value("Work Order", self.work_order, "production_item")
			operation_id = ""
			for row in work_order_doc.operations:
				if row.operation == self.operation:
					operation_id = row.name

			jobcardDoc = frappe.new_doc("Job Card")
			jobcardDoc.work_order = self.work_order
			jobcardDoc.production_item = production_item

			jobcardDoc.for_quantity = self.qty
			
			jobcardDoc.wip_warehouse = wip_warehouse
			jobcardDoc.operation = self.operation
			jobcardDoc.workstation = self.workstation
			jobcardDoc.operation_id = operation_id

			jobcardDoc.append("time_logs",{
				"completed_qty": self.qty,
			})

			if work_order_doc.transfer_material_against == "Work Order" or work_order_doc.skip_transfer:
				return

			for d in work_order_doc.required_items:
				if not d.operation:
					frappe.throw(
						_("Row {0} : Operation is required against the raw material item {1}").format(
							d.idx, d.item_code
						)
					)

				if self.operation == d.operation:
					
					jobcardDoc.append(
						"items",
						{
							"item_code": d.item_code,
							"source_warehouse": d.source_warehouse,
							"uom": frappe.db.get_value("Item", d.item_code, "stock_uom"),
							"item_name": d.item_name,
							"description": d.description,
							"required_qty": (d.required_qty * flt(self.qty)) / work_order_doc.qty,
							"rate": d.rate,
							"amount": d.amount,
						},
					)

			jobcardDoc.remarks = self.name
			jobcardDoc.save()
			if self.auto_transfer_rm == 1:
				for row in work_order_doc.operations:
					if row.idx == 1 and row.operation == self.operation:
						se_doc_name = self.transfer_rm()
						se_doc = frappe.get_doc("Stock Entry", se_doc_name)
						for m in se_doc.items:
							for n in jobcardDoc.items:
								if m.item_code == n.item_code:
									jobcardDoc.db_set('transferred_qty', self.qty)

			jobcardDoc.reload()
			jobcardDoc.submit()
			self.db_set("job_card", jobcardDoc.name)
			for row in work_order_doc.operations:
				if row.operation == self.operation:
					self.db_set('pending_qty', work_order_doc.qty - ( row.completed_qty + self.qty))
		
		
	

	def transfer_rm(self):
		woDoc = frappe.get_cached_doc('Work Order', self.work_order)
		st = frappe.new_doc('Stock Entry')
		st.posting_date = self.posting_date
		st.stock_entry_type = 'Material Transfer for Manufacture'
		st.work_order = woDoc.name
		st.from_bom = 1
		st.bom_no = self.bom
		st.to_warehouse = woDoc.wip_warehouse
		st.fg_completed_qty = self.qty
		st.get_items()
		st.save()
		st.work_order = woDoc.name
		st.save()
		st.submit()
		self.db_set("Stock Entry", st.name)
		return st.name



	def before_submit(self):
		wodoc = frappe.get_doc("Work Order",self.work_order)
		if self.item != wodoc.production_item:
			frappe.throw("Item does not match with Work Order Item")

		if self.bom:
			if self.bom != wodoc.bom_no:
				frappe.throw("BOM does not match with Work Order BOM	")

		if self.qty > wodoc.qty:
			frappe.throw("Cannot produce qty more than Work Order Qty")
		

    
	def on_cancel(self):
		jobcard_doc = frappe.get_doc("Job Card",self.job_card)
		if jobcard_doc:
			jobcard_doc.cancel()
			self.db_set("job_card","")

		if self.stock_entry:
			stock_entry = frappe.get_doc("Stock Entry",self.stock_entry)
			stock_entry.cancel()
			self.db_set("stock_entry","")

		# frappe.msgprint("Cancelled")
