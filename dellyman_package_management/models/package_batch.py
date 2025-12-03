from odoo import models, fields, api, _

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    name = fields.Char(string='Batch Number', required=True, readonly=True, default='New')
    sequence = fields.Char(string='Sequence', readonly=True)
    arrival_date = fields.Date(default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name','New') == 'New':
                seq = self.env['ir.sequence'].next_by_code('package.batch') or '/'
                vals['sequence'] = seq
                vals['name'] = vals.get('name', seq)
        return super(PackageBatch, self).create(vals_list)
