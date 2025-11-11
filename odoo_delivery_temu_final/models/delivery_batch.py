from odoo import models, fields, api

class DeliveryBatch(models.Model):
    _name = 'delivery.batch'
    _description = 'Incoming Delivery Batch'
    _rec_name = 'name'

    name = fields.Char(string='Batch Number', required=True, copy=False, readonly=True, default='New')
    arrival_date = fields.Datetime(string='Arrival Date', default=fields.Datetime.now)
    package_ids = fields.One2many('delivery.package', 'batch_id', string='Packages')
    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'), ('processed', 'Processed')], default='draft')
    location_id = fields.Many2one('temu.location', string='Default Location')
    note = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env.ref('odoo_delivery_temu_final.seq_delivery_batch', raise_if_not_found=False)
            vals['name'] = seq.next_by_id() if seq else self.env['ir.sequence'].next_by_code('delivery.batch')
        return super().create(vals)

    def action_receive(self):
        for rec in self:
            rec.state = 'received'
            rec.package_ids.write({'status': 'received'})

    def action_process(self):
        for rec in self:
            rec.state = 'processed'
            rec.package_ids.write({'status': 'in_sorting'})
