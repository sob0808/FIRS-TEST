from odoo import models, fields, api, _

class PackageBatch(models.Model):
    _name = "package.batch"
    _description = "Package Batch"
    _rec_name = "name"

    # Basic fields
    name = fields.Char(string='Batch Number', required=True, readonly=True, default='New')
    sequence = fields.Char(string='Internal Sequence', readonly=True)

    # Newly added fields to fix XML errors
    date_created = fields.Datetime(string="Created On", default=fields.Datetime.now)
    package_count = fields.Integer(string="Package Count", compute="_compute_package_count", store=True)

    # Existing field
    arrival_date = fields.Date(string="Arrival Date", default=fields.Date.context_today)

    # Packages
    package_ids = fields.One2many('package.order', 'batch_id', string='Packages')

    @api.depends('package_ids')
    def _compute_package_count(self):
        """Compute number of packages in the batch."""
        for rec in self:
            rec.package_count = len(rec.package_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Safe for multi-create (Odoo 17/18 standard)."""
        seq_model = self.env['ir.sequence']
        for vals in vals_list:

            # Assign sequence if not provided
            if not vals.get('sequence'):
                next_seq = seq_model.next_by_code('package.batch') or '/'
                vals['sequence'] = next_seq

            # Replace name if default "New"
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals['sequence']

        return super().create(vals_list)
