from odoo import models, fields, api, _

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    name = fields.Char(string='Batch Number', required=True, readonly=True, default='New')
    sequence = fields.Char(string='Internal Sequence', readonly=True)
    arrival_date = fields.Date(string="Arrival Date", default=fields.Date.context_today)
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')

    @api.model_create_multi
    def create(self, vals_list):
        """Safe for multi-create (Odoo 17/18 standard)."""
        seq_model = self.env['ir.sequence']
        for vals in vals_list:
            # Assign sequence only when needed
            if not vals.get('sequence'):
                next_seq = seq_model.next_by_code('package.batch') or '/'
                vals['sequence'] = next_seq

            # Replace name if default "New"
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals['sequence']

        return super().create(vals_list)
