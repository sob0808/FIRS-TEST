
from odoo import models, fields

class PortalPayslipSettings(models.Model):
    _name='portal.payslip.settings'
    _description='Portal Payslip Settings'

    signature_attachment=fields.Many2one('ir.attachment')
    watermark_attachment=fields.Many2one('ir.attachment')
    notes=fields.Text()
