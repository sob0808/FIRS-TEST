
{
 'name': 'Portal Payslip - Full Feature SaaS (OPL-1 Branded)',
 'version': '1.0.0',
 'license': 'OPL-1',
 'summary': 'Full-feature payslip portal with filters, attachments, PDF download, settings (SaaS-safe)',
 'depends': ['hr_payroll','website'],
 'data': [
   'security/portal_payslip_security.xml',
   'views/portal_payslip_templates.xml',
   'views/portal_payslip_settings_views.xml',
   'views/portal_payslip_settings_action.xml',
   'views/website_menu.xml'
 ],
 'installable': True
}
