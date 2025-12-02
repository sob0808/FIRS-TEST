
from odoo import models, fields

class PackageBatch(models.Model):
    _name = 'package.batch'
    _description = 'Package Batch'

    name = fields.Char(required=True)
    arrival_date = fields.Date()
    package_ids = fields.One2many('package.order','batch_id')
    package_count = fields.Integer(compute='_compute_count')

    def _compute_count(self):
        for r in self:
            r.package_count = len(r.package_ids)
