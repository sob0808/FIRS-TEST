
from odoo import models, fields

class PackageLocation(models.Model):
    _name = "package.location"
    _description = "Package Storage Location"

    name = fields.Char(required=True)
    description = fields.Text()
