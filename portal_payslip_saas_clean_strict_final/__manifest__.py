{
    'name': 'Portal Payslip - SaaS Clean Strict (Final)',
    'version': '1.0.2',
    'summary': 'Employee payslip portal page for Odoo SaaS (strict portal auth, friendly message)',
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
            '/portal_payslip_saas_clean_strict_final/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
