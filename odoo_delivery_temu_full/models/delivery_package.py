from odoo import models, fields, api

class DeliveryPackage(models.Model):
    _name = 'delivery.package'
    _description = 'Delivery Package'

    name = fields.Char(string='Tracking / Barcode', required=True)
    sender = fields.Char(string='Sender', default='TEMU')
    recipient_name = fields.Char(string='Recipient')
    weight = fields.Float(string='Weight (kg)')
    batch_id = fields.Many2one('delivery.batch', string='Batch')
    location_id = fields.Many2one('stock.location', string='Current Location')
    status = fields.Selection([('draft', 'Draft'), ('received', 'Received'), ('in_sorting', 'In Sorting'), ('dispatched', 'Dispatched')], default='draft')
    scan_time = fields.Datetime(string='Scanned At', default=fields.Datetime.now)
    barcode = fields.Char(string='Barcode')
    note = fields.Text(string='Notes')

    _sql_constraints = [('unique_name_batch', 'UNIQUE(name, batch_id)', 'Tracking / Barcode must be unique in the batch.')]

    @api.model
    def create(self, vals):
        if not vals.get('scan_time'):
            vals['scan_time'] = fields.Datetime.now()
        return super().create(vals)

    def action_assign_default_location(self):
        for rec in self:
            if rec.batch_id and rec.batch_id.location_id:
                rec.location_id = rec.batch_id.location_id
