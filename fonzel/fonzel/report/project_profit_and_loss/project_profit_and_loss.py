# Copyright (c) 2025, Matiyas Solutions LLP and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 80},
        {"label": "Qty Sold", "fieldname": "qty_sold", "fieldtype": "Float", "precision": 2,"width": 100},
        {"label": "Selling Amount", "fieldname": "selling_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Raw Material Cost", "fieldname": "manufacturing_cost", "fieldtype": "Currency", "width": 130},
        {"label": "Labour Cost", "fieldname": "labour_cost", "fieldtype": "Currency", "width": 110},
        {"label": "Other Expenses", "fieldname": "other_expenses", "fieldtype": "Currency", "width": 120},
        {"label": "Freight Charge", "fieldname": "freight_charge", "fieldtype": "Currency", "width": 150},
        {"label": "Transportation Charge", "fieldname": "transportation_charge", "fieldtype": "Currency", "width": 150},
        {"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 120},
        {"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": "Profit %", "fieldname": "profit_percent", "fieldtype": "Percent", "precision": 2, "width": 90},
    ]


def get_data(filters):
    values = {}
    conditions = ""
    if filters and filters.get("project"):
        conditions += " AND si.project = %(project)s"
        values["project"] = filters.get("project")

    project_company_join = ""
    project_company_filter = ""
    if filters and filters.get("company"):
        project_company_join = " LEFT JOIN tabProject p ON si.project = p.name "
        project_company_filter = " AND p.company = %(company)s "
        values["company"] = filters.get("company")

    sales = frappe.db.sql(f"""
        SELECT
            si.project,
            sii.item_code,
            sii.item_name,
            sii.uom,
            SUM(sii.qty) AS qty_sold,
            SUM(sii.base_net_amount) AS selling_amount
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        {project_company_join}
        WHERE si.docstatus = 1
          AND si.project IS NOT NULL
          AND si.project != ''
          {conditions} {project_company_filter}
        GROUP BY si.project, sii.item_code
        ORDER BY si.project, sii.item_code
    """, values=values, as_dict=True)

    data = []
    last_project = None
    project_totals = {}
    project_header_index = None


    for s in sales:
        if s.project != last_project:
            if last_project and project_header_index is not None:
                data[project_header_index].update(project_totals)

            project_totals = {
                "qty_sold": 0,
                "selling_amount": 0,
                "manufacturing_cost": 0,
                "labour_cost": 0,
                "other_expenses": 0,
                "freight_charge": 0,
                "transportation_charge": 0,
                "total_cost": 0,
                "profit": 0,
                "profit_percent": 0,
            }

            project_header_index = len(data)
            data.append({
                "project": s.project,
                "bold": 1       
            })

            last_project = s.project

        manufacturing_cost = frappe.db.sql("""
            SELECT SUM(sed.valuation_rate * sed.qty)
            FROM `tabStock Entry Detail` sed
            JOIN `tabStock Entry` se ON sed.parent = se.name
            WHERE se.docstatus = 1 AND se.purpose = 'Manufacture'
              AND se.project = %s AND sed.item_code = %s
        """, (s.project, s.item_code))[0][0] or 0

        work_order = frappe.db.get_list(
            "Stock Entry",
            {"purpose": "Manufacture", "docstatus": 1, "project": s.project},
            "work_order"
        )

        total_transport_charge = 0
        total_freight_charge = 0

        company = frappe.get_value("Project", s.project, "company")
        company_abbr = frappe.get_value("Company", company, "abbr")

        transport_account = f"Tranport Charges - {company_abbr}"
        freight_account = f"Freight and Forwarding Charges - {company_abbr}"

        def get_charge(account, item_code):
            row = frappe.db.sql("""
                SELECT 
                    SUM(lci.applicable_charges) AS amt,
                    SUM(lci.qty) AS qty
                FROM `tabLanded Cost Voucher` lcv
                JOIN `tabLanded Cost Item` lci ON lci.parent = lcv.name
                JOIN `tabLanded Cost Taxes and Charges` t ON t.parent = lcv.name
                JOIN `tabLanded Cost Purchase Receipt` lpr ON lpr.parent = lcv.name
                JOIN `tabPurchase Receipt` pr ON pr.name = lpr.receipt_document
                WHERE lcv.docstatus = 1
                  AND t.expense_account = %s
                  AND pr.project = %s
                  AND lci.item_code = %s
            """, (account, s.project, item_code), as_dict=True)
            return row[0] if row else None

        # Loop work order items
        operating_cost = 0
        for wo in work_order:
            operating_cost += frappe.db.get_value("Work Order",{"name":wo.work_order,"docstatus": 1, "project": s.project},"total_operating_cost") 
            items = frappe.db.get_all(
                "Work Order Item",
                {"parent": wo.work_order},
                ["item_code", "required_qty"]
            )

            for item in items:

                t = get_charge(transport_account, item.item_code)
                if t and t.qty:
                    total_transport_charge += (t.amt / t.qty) * item.required_qty

                f = get_charge(freight_account, item.item_code)
                if f and f.qty:
                    total_freight_charge += (f.amt / f.qty) * item.required_qty

        transportation_charge = total_transport_charge
        freight_charge = total_freight_charge

        manufacturing_cost -= (freight_charge + transportation_charge + operating_cost)

        labour_cost = frappe.db.sql("""
            SELECT SUM(tsd.billing_amount)
            FROM `tabTimesheet Detail` tsd
            LEFT JOIN `tabTask` t ON tsd.task = t.name
            WHERE (tsd.project = %s OR t.project = %s)
        """, (s.project, s.project))[0][0] or 0

        # operating_cost = frappe.db.sql("""
        #     SELECT SUM(bo.operating_cost)
        #     FROM `tabBOM` b
        #     JOIN `tabBOM Operation` bo ON bo.parent = b.name
        #     WHERE b.docstatus = 1 AND b.item = %s
        # """, (s.item_code,))[0][0] or 0

        labour_cost += operating_cost

        other_expenses = frappe.db.sql("""
            SELECT SUM(total_sanctioned_amount)
            FROM `tabExpense Claim`
            WHERE project = %s AND docstatus = 1
        """, (s.project,))[0][0] or 0

        je_cost = frappe.db.sql("""
            SELECT SUM(debit)
            FROM `tabJournal Entry Account`
            WHERE project = %s
        """, (s.project,))[0][0] or 0

        other_expenses += (je_cost or 0)

        total_cost = manufacturing_cost + labour_cost + other_expenses + transportation_charge + freight_charge
        profit = s.selling_amount - total_cost
        profit_percent = (profit / s.selling_amount * 100) if s.selling_amount else 0

        project_totals["qty_sold"] += s.qty_sold or 0
        project_totals["selling_amount"] += s.selling_amount or 0
        project_totals["manufacturing_cost"] += manufacturing_cost or 0
        project_totals["labour_cost"] += labour_cost or 0
        project_totals["other_expenses"] += other_expenses or 0
        project_totals["freight_charge"] += freight_charge or 0
        project_totals["transportation_charge"] += transportation_charge or 0
        project_totals["total_cost"] += total_cost or 0
        project_totals["profit"] += profit or 0

        if project_totals["selling_amount"]:
            project_totals["profit_percent"] = (
                project_totals["profit"] / project_totals["selling_amount"] * 100
            )

        data.append({
            "project": "",
            "item_code": s.item_code,
            "item_name": s.item_name,
            "uom": s.uom,
            "qty_sold": s.qty_sold,
            "selling_amount": s.selling_amount,
            "manufacturing_cost": manufacturing_cost,
            "labour_cost": labour_cost,
            "other_expenses": other_expenses,
            "freight_charge": freight_charge,
            "transportation_charge": transportation_charge,
            "total_cost": total_cost,
            "profit": profit,
            "profit_percent": profit_percent,
            "indent": 1,
            "bold": 0
        })

    if last_project and project_header_index is not None:
        data[project_header_index].update(project_totals)

    return data
