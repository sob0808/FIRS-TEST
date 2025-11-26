{
    "name": "Mattobell Portal Payslip",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Employee portal payslip viewer (auth=user) - Matt O'Bell",
    "category": "Human Resources",
    "depends": ["hr_payroll","website"],
    "data": [
        "security/portal_payslip_security.xml",
        "views/portal_payslip_templates.xml",
        "views/portal_payslip_settings_views.xml",
        "views/portal_payslip_settings_action.xml",
        "views/website_menu.xml"
    ],
    "installable": True,
    "application": False
}
