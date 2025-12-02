
from odoo import models, fields

class PackageLocation(models.Model):
    _name = "package.location"
    _description = "Package Location"

    name = fields.Char(required=True)
