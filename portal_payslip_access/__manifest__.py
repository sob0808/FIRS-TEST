{
    'name': 'Portal Payslip Access',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Allow employees to view and download their payslips from the portal',
    'depends': ['hr_payroll', 'portal'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_menu.xml',
        'views/portal_payslip_templates.xml',
    ],
    'installable': True,
}
