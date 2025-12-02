
from odoo import models, fields

class PackageBatch(models.Model):
    _name = 'package.batch'
    _description = 'Package Batch'
    _rec_name = 'name'

    name = fields.Char(required=True)
    arrival_date = fields.Date(default=fields.Date.context_today)
    package_ids = fields.One2many('package.order','batch_id', string='Packages')
    package_count = fields.Integer(compute='_compute_count', store=False)

    def _compute_count(self):
        for r in self:
            r.package_count = len(r.package_ids)
