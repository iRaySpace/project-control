# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "project_control"
app_title = "Project Control"
app_publisher = "9T9IT"
app_description = "An ERPNext app"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@9t9it.com"
app_license = "MIT"

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Project-naming_series",
                    "Project-pc_budget_sb",
                    "Project-pc_budgets",
                    "Project-pc_budget_total"
                ]
            ]
        ]
    }
]

doctype_js = {
    "Project": "public/js/project.js"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Project": {
        "validate": "project_control.doc_events.project.validate"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"project_control.tasks.all"
# 	],
# 	"daily": [
# 		"project_control.tasks.daily"
# 	],
# 	"hourly": [
# 		"project_control.tasks.hourly"
# 	],
# 	"weekly": [
# 		"project_control.tasks.weekly"
# 	]
# 	"monthly": [
# 		"project_control.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "project_control.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "project_control.event.get_events"
# }

