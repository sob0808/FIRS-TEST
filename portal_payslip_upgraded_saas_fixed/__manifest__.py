{
    'name': 'Portal Payslip Access - SaaS Fixed',
    'version': '1.4',
    'summary': 'SaaS-stable portal payslip dashboard with filters, attachments, signature/watermark',
    'depends': ['hr_payroll', 'portal'],
    'data': [
        'security/portal_payslip_security.xml',
        'views/portal_menu.xml',
        'views/portal_payslip_templates.xml',
        'views/portal_payslip_settings_views.xml',
        'views/portal_payslip_settings_action.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_upgraded_saas_fixed/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
}
