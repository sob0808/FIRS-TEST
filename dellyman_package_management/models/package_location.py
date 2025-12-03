from odoo import models, fields, api

class PackageLocation(models.Model):
    _name = "package.location"
    _description = "Package Location"
    _rec_name = "name"

    name = fields.Char(required=True, string="Location Name")
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    package_ids = fields.One2many('package.order', 'location_id', string='Packages')
    package_count = fields.Integer(string='Number of Packages', compute='_compute_package_count', store=True)

    @api.depends('package_ids')
    def _compute_package_count(self):
        for record in self:
            record.package_count = len(record.package_ids)
