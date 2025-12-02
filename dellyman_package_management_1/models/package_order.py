
from odoo import models, fields, api

class PackageOrder(models.Model):
    _name = 'package.order'
    _description = 'Package'

    name = fields.Char(required=True)
    ord_id = fields.Char()
    batch_id = fields.Many2one('package.batch')
    current_status = fields.Selection([
        ('received','Received'),
        ('assigned','Assigned'),
        ('picked','Picked'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('awaiting_return','Awaiting Return'),
        ('returned','Returned')
    ], default='received')

    package_description = fields.Char()
    customer_name = fields.Char()
    customer_phone = fields.Char()
    customer_address = fields.Char()

    location_id = fields.Many2one('package.location', string='Location')

    def action_set_status(self):
        for r in self:
            ctx = self.env.context
            if 'status' in ctx:
                r.current_status = ctx['status']
