from odoo import models, fields, api

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    name = fields.Char(required=True, default='New')
    sequence = fields.Char(string='Batch Sequence', readonly=True)
    arrival_date = fields.Date(default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('package.batch') or '/'
            vals['name'] = vals.get('name', vals['sequence'])
        return super(PackageBatch, self).create(vals)
