from odoo import models, fields, api

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    name = fields.Char(required=True, default='New')
    sequence = fields.Char(string='Batch Sequence', readonly=True)
    arrival_date = fields.Date(default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')

    @api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # your code here, applied per record
        pass
    return super().create(vals_list)
