from odoo import models, fields

class PackageLocation(models.Model):
    _name = "package.location"
    _description = "Package Location"

    name = fields.Char(required=True)
    code = fields.Char(string='Code')
    description = fields.Text()
    package_ids = fields.One2many('package.order', 'location_id', string='Packages')
