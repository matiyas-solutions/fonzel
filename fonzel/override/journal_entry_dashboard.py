from frappe import _


def get_dashboard_for_project(data):
	data["transactions"].append(
		{"label": _("Account"), "items": ["Journal Entry"]},
	)
    
	return data