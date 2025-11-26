{
    "name": "Mattobell Payslip - Auto DMS Upload & Share",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Auto-upload payslip PDF to Documents and share with employee portal user.",
    "category": "Human Resources",
    "depends": ["website","hr_payroll","portal","documents"],
    "data": [
        "views/portal_payslip_templates.xml",
        "views/website_menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False
}
