{
    "name": "Mattobell Portal Payslip (Strict + Autolink)",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Portal payslips with strict user=employee requirement and exact-email autolink.",
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
