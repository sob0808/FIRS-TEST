
from odoo import models, fields, api

class PackageOrder(models.Model):
    _name = 'package.order'
    _description = 'Package Order'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(required=True)
    ord_id = fields.Char()
    batch_id = fields.Many2one('package.batch', string='Batch')
    location_id = fields.Many2one('package.location', string='Location')
    package_description = fields.Text()
    customer_name = fields.Char()
    customer_phone = fields.Char()
    customer_address = fields.Char()

    current_status = fields.Selection([
        ('received','Received'),
        ('assigned','Assigned'),
        ('picked','Picked'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('awaiting_return','Awaiting Return'),
        ('returned','Returned')
    ], default='received', tracking=True)

    def action_set_status(self):
        for rec in self:
            status = self.env.context.get('status')
            if status:
                old = rec.current_status
                rec.current_status = status
                # post message in chatter
                rec.message_post(body=f"Status changed from {old} to {status}", subtype_xmlid='mail.mt_note')
