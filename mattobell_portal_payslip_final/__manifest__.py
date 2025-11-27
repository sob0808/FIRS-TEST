{
    "name": "Mattobell Portal Payslip (Final)",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Employee payslips on portal (/my/payslips) - Matt O'Bell",
    "category": "Human Resources",
    "depends": ["website","hr_payroll","portal"],
    "data": [
        "views/portal_payslip_templates.xml",
        "views/website_menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False
}
