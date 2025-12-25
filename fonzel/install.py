import frappe

POST_INSTALL_PATCHES = [
    "journal_entry",
]

def after_install():
    run_post_install_patches()

def run_post_install_patches():
    frappe.flags.in_patch = True

    try:
        for patch in POST_INSTALL_PATCHES:
            frappe.get_attr(f"fonzel.patches.{patch}.execute")()

    finally:
        frappe.flags.in_patch = False