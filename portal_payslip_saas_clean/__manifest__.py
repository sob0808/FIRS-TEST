{
    'name': 'Portal Payslip - SaaS Clean',
    'version': '1.0.0',
    'summary': 'Employee payslip portal page (SaaS-clean) with website menu link',
    'category': 'Human Resources',
    'depends': ['hr_payroll', 'portal', 'website'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
        'views/website_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_saas_clean/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
