
from odoo import models, fields

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"

    name = fields.Char(required=True)
    description = fields.Text()
