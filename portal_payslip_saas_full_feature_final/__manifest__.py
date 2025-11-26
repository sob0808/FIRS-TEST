{
    "name": "Portal Payslip - Full Feature SaaS Safe",
    "version": "1.0.0",
    "summary": "Employee payslip portal page (auth=user) with filters, attachments, PDF download, settings (SaaS-safe)",
    "category": "Human Resources",
    "depends": ["hr_payroll","website"],
    "data": [
        "security/portal_payslip_security.xml",
        "views/portal_payslip_templates.xml",
        "views/portal_payslip_settings_views.xml",
        "views/portal_payslip_settings_action.xml",
        "views/website_menu.xml"
    ],
    "installable": true,
    "application": false
}
