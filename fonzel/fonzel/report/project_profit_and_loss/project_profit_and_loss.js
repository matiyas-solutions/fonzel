// Copyright (c) 2025, Matiyas Solutions LLP and contributors
// For license information, please see license.txt

frappe.query_reports["Project Profit and Loss"] = {
	"filters": [
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            reqd: 1
        },
        {
            fieldname: "project",
            label: "Project",
            fieldtype: "Link",
            options: "Project",
            reqd: 0
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.get_today()
        }
    ],
	tree: true,                  
    name_field: "project",       // ✔ main field
    parent_field: "parent_project", // if not needed keep null/blank
    initial_depth: 1,

    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);
        if (data && data.bold == 1) {
            value = $(`<span>${value}</span>`);
            value = $(value).css("font-weight", "bold");
            value = value.wrap("<p></p>").parent().html();
        }

        return value;
    }
};
