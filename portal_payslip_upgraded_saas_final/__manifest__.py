{
    'name': 'Portal Payslip Access - SaaS Final',
    'version': '1.5',
    'summary': 'SaaS-safe portal payslip dashboard with portal home card, filters, attachments, signature/watermark',
    'depends': ['hr_payroll', 'portal'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
        'views/portal_home_card.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_upgraded_saas_final/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
