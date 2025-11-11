from odoo import models, fields, api

class ScanWizard(models.TransientModel):
    _name = 'delivery.scan.wizard'
    _description = 'Scan Package Wizard'

    batch_id = fields.Many2one('delivery.batch', string='Batch', required=True)
    barcode = fields.Char(string='Scan / Enter Tracking', required=True)
    recipient_name = fields.Char(string='Recipient')
    weight = fields.Float(string='Weight (kg)')
    assign_location = fields.Boolean(string='Assign batch default location', default=True)

    def action_add_package(self):
        Package = self.env['delivery.package']
        vals = {
            'name': self.barcode,
            'barcode': self.barcode,
            'recipient_name': self.recipient_name,
            'weight': self.weight,
            'batch_id': self.batch_id.id,
        }
        pkg = Package.create(vals)
        if self.assign_location and self.batch_id.location_id:
            pkg.location_id = self.batch_id.location_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.batch',
            'res_id': self.batch_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
