from odoo import models, fields, api

class PackageBatch(models.Model):
    _name = 'package.batch'
    _description = 'Package Batch'

    name = fields.Char(string='Batch Number', required=True, copy=False, default=lambda self: self._default_sequence())
    arrival_date = fields.Date(string='Arrival Date', default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')
    expected_quantity = fields.Integer(string='Expected Quantity')
    total_packages = fields.Integer(string='Total Packages', compute='_compute_package_counts')
    delivered_packages = fields.Integer(string='Delivered Packages', compute='_compute_package_counts')
    returned_packages = fields.Integer(string='Returned Packages', compute='_compute_package_counts')
    status = fields.Selection([('open','Open'), ('closed','Closed')], default='open')

    def _default_sequence(self):
        seq = self.env['ir.sequence'].search([('name','=','Package Batch')], limit=1)
        if seq:
            return seq.next_by_id()
        return False

    @api.depends('package_ids', 'package_ids.current_status')
    def _compute_package_counts(self):
        for batch in self:
            batch.total_packages = len(batch.package_ids)
            batch.delivered_packages = len(batch.package_ids.filtered(lambda p: p.current_status == 'delivered'))
            batch.returned_packages = len(batch.package_ids.filtered(lambda p: p.current_status == 'returned'))
            # Auto close when all packages are final
            if batch.package_ids and all(p.current_status in ('delivered','returned','archived') for p in batch.package_ids):
                batch.status = 'closed'
