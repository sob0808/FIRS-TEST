{
    'name': 'Portal Payslip Access - Upgraded',
    'version': '1.2',
    'category': 'Human Resources',
    'summary': 'Enhanced portal payslip dashboard with filters, attachments, and PDF watermark/signature',
    'depends': ['hr_payroll', 'portal', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_payslip_security.xml',
        'views/portal_menu.xml',
        'views/portal_payslip_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/portal_payslip_upgraded/static/src/css/portal_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
