from odoo import models, fields, api

class PortalPayslipSettings(models.Model):
    _name = 'portal.payslip.settings'
    _description = 'Portal Payslip Settings'
    _rec_name = 'id'

    signature_attachment = fields.Many2one('ir.attachment', string='HR Signature (PDF)')
    watermark_attachment = fields.Many2one('ir.attachment', string='Payslip Watermark (PDF)')
    notes = fields.Text(string='Notes')
