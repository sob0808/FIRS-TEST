from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PackageOrder(models.Model):
    _name = 'package.order'
    _inherit = ['mail.thread']
    _description = 'Package Order / Item'

    name = fields.Char(string='Tracking ID', required=True, copy=False)
    ord_id = fields.Char(string='ORD ID')
    package_description = fields.Text(string='Description')
    customer_name = fields.Char(string='Customer Name')
    customer_phone = fields.Char(string='Customer Phone')
    customer_address = fields.Text(string='Customer Address')
    current_status = fields.Selection([
        ('draft','Draft'),
        ('received','Received'),
        ('assigned','Assigned to Rider'),
        ('picked','Package Picked'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('awaiting_return','Awaiting Return'),
        ('returned','Returned'),
        ('archived','Archived'),
    ], default='draft', string='Status', tracking=True)
    batch_id = fields.Many2one('package.batch', string='Batch', ondelete='set null')
    rider_id = fields.Many2one('res.partner', string='Rider')
    date_received = fields.Datetime(string='Date Received')
    date_delivered = fields.Datetime(string='Date Delivered')

    _sql_constraints = [
        ('tracking_unique', 'unique(name)', 'Tracking ID must be unique!')
    ]

    @api.model
    def create_from_scan(self, tracking_id, batch=None):
        """Create or update a package record from a scanned tracking ID."""
        package = self.search([('name','=',tracking_id)], limit=1)
        vals = {'name': tracking_id}
        if batch:
            vals['batch_id'] = batch.id
        if not package:
            package = self.create(vals)
        else:
            package.write(vals)
        # Placeholder: try sync with Dellyman connector (non-blocking)
        try:
            package._sync_from_dellyman()
        except Exception:
            pass
        return package

    def _sync_from_dellyman(self):
        connector = self.env.get('dellyman.connector')
        if not connector:
            return
        for rec in self:
            data = self.env['dellyman.connector'].fetch_package_by_tracking(rec.name)
            if not data:
                continue
            rec.write({
                'ord_id': data.get('ord_id') or data.get('order_id'),
                'package_description': data.get('description') or data.get('package_description'),
                'customer_name': (data.get('customer') or {}).get('name') or data.get('customer_name'),
                'customer_phone': (data.get('customer') or {}).get('phone') or data.get('customer_phone'),
                'customer_address': (data.get('customer') or {}).get('address') or data.get('customer_address'),
                'current_status': data.get('status') or rec.current_status,
            })

    def action_set_status(self):
        """Set status from context {'status': '...'} passed by buttons.
        Posts a chatter message including the user's name."""
        status = self.env.context.get('status')
        if not status:
            raise UserError('No status provided in context.')
        status_labels = {
            'received': 'Received',
            'assigned': 'Assigned',
            'picked': 'Picked',
            'in_transit': 'In Transit',
            'delivered': 'Delivered',
            'awaiting_return': 'Awaiting Return',
            'returned': 'Returned',
        }
        for rec in self:
            old_status = rec.current_status or 'none'
            if status not in dict(rec._fields['current_status'].selection):
                raise UserError('Invalid status: %s' % status)
            rec.current_status = status
            if status == 'delivered':
                rec.date_delivered = fields.Datetime.now()
            if rec.batch_id:
                try:
                    rec.batch_id._compute_package_counts()
                except Exception:
                    pass
            # post chatter message with user name
            old_lbl = status_labels.get(old_status, old_status)
            new_lbl = status_labels.get(status, status)
            user_name = self.env.user.name
            rec.message_post(body=f"Status changed from <b>{old_lbl}</b> to <b>{new_lbl}</b> by {user_name}.")
    def action_set_status(self):
        status=self.env.context.get('status')
        for rec in self:
            rec.status=status