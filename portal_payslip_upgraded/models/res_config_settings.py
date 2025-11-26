from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    signature_attachment = fields.Many2one('ir.attachment', string='HR Signature (PDF)')
    watermark_attachment = fields.Many2one('ir.attachment', string='Payslip Watermark (PDF)')

    def get_values(self):
        res = super().get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        sig_id = IrConfig.get_param('portal_payslip_upgraded.signature_attachment_id')
        wm_id = IrConfig.get_param('portal_payslip_upgraded.watermark_attachment_id')
        res.update({
            'signature_attachment': int(sig_id) if sig_id else False,
            'watermark_attachment': int(wm_id) if wm_id else False,
        })
        return res

    def set_values(self):
        super().set_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        IrConfig.set_param('portal_payslip_upgraded.signature_attachment_id', str(self.signature_attachment.id) if self.signature_attachment else '')
        IrConfig.set_param('portal_payslip_upgraded.watermark_attachment_id', str(self.watermark_attachment.id) if self.watermark_attachment else '')
