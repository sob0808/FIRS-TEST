{
    'name': 'Portal Payslip Access - Upgraded (SaaS Safe)',
    'version': '1.3',
    'category': 'Human Resources',
    'summary': 'Enhanced portal payslip dashboard (SaaS-optimized settings model)',
    'depends': ['hr_payroll', 'portal', 'base'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_menu.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_upgraded_saas/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
