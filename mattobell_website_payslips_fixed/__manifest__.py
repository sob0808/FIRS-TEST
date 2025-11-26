{
    "name": "Employee Payslip Portal (Mattobell)",
    "version": "1.1.0",
    "license": "OPL-1",
    "summary": "Website-based employee payslip portal with custom Mattobell PDF.",
    "depends": ["website","hr_payroll"],
    "data": [
        "views/payslip_templates.xml",
        "views/website_menu.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True
}
