{
    'name': 'Portal Payslip - Full Feature SaaS (Auth User)',
    'version': '1.0.0',
    'summary': 'Employee payslip portal page (auth=user) with filters, attachments, PDF download, settings',
    'category': 'Human Resources',
    'depends': ['hr_payroll','website'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
        'views/website_menu.xml',
        'views/portal_payslip_assets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_full_feature_final/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
