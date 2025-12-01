from odoo import models, fields, api
from odoo.exceptions import UserError

class PackageBatch(models.Model):
    _name = 'package.batch'
    _description = 'Package Batch'

    name = fields.Char(string='Batch Number', required=True, copy=False, default=lambda self: self._default_sequence())
    arrival_date = fields.Date(string='Arrival Date', default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')
    expected_quantity = fields.Integer(string='Expected Quantity')
    total_packages = fields.Integer(string='Total Packages', compute='_compute_package_counts', store=True)
    delivered_packages = fields.Integer(string='Delivered Packages', compute='_compute_package_counts', store=True)
    returned_packages = fields.Integer(string='Returned Packages', compute='_compute_package_counts', store=True)
    status = fields.Selection([('open','Open'), ('in_progress','In Progress'), ('completed','Completed'), ('archived','Archived')], default='open', string='Status')

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
            # Auto update status
            if not batch.package_ids:
                batch.status = 'open'
            else:
                statuses = set(batch.package_ids.mapped('current_status'))
                if statuses.issubset({'delivered','returned','archived'}):
                    batch.status = 'completed'
                elif 'in_transit' in statuses or 'picked' in statuses or 'assigned' in statuses:
                    batch.status = 'in_progress'
                else:
                    batch.status = 'open'

    def action_close_batch(self):
        for batch in self:
            if batch.package_ids and not all(p.current_status in ('delivered','returned','archived') for p in batch.package_ids):
                raise UserError('Cannot close batch until all packages are delivered or returned.')
            batch.status = 'archived'
