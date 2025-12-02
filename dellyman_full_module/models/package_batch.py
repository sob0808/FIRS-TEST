
from odoo import models, fields

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    name = fields.Char(required=True)
    arrival_date = fields.Date(default=fields.Date.today)
    package_ids = fields.One2many("package.order","batch_id")
    package_count = fields.Integer(compute="_compute_count")

    def _compute_count(self):
        for rec in self:
            rec.package_count = len(rec.package_ids)
