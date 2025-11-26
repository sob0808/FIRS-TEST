{
    "name": "Mattobell Portal Payslip (Email Match)",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Portal payslips where matching is done by employee.work_email == portal user email.",
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
