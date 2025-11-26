{
    "name": "Employee Payslip Portal (Mattobell)",
    "version": "1.0.0",
    "license": "OPL-1",
    "summary": "Website-based payslip viewer for employees (Odoo.sh compatible)",
    "category": "Human Resources",
    "depends": ["website","hr_payroll"],
    "data": [
        "views/payslip_templates.xml",
        "views/website_menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": False
}
