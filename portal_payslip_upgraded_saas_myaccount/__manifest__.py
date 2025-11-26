{
    'name': 'Portal Payslip Access - SaaS MyAccount',
    'version': '1.6',
    'summary': 'SaaS-safe portal payslip with My Account link, dashboard, filters, attachments, watermark/signature',
    'depends': ['hr_payroll', 'portal'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
        'views/portal_account_link.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_upgraded_saas_myaccount/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
