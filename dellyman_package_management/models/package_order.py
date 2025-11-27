from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PackageOrder(models.Model):
    _name = 'package.order'
    _description = 'Package Order / Item'

    name = fields.Char(string='Tracking ID', required=True, copy=False)
    ord_id = fields.Char(string='ORD ID')
    package_description = fields.Text(string='Description')
    customer_name = fields.Char()
    customer_phone = fields.Char()
    customer_address = fields.Text()
    current_status = fields.Selection([
        ('received','Received at Warehouse'),
        ('assigned','Assigned to Rider'),
        ('picked','Package Picked'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('awaiting_return','Awaiting Return'),
        ('returned','Returned'),
        ('archived','Archived'),
    ], default='received')
    batch_id = fields.Many2one('package.batch', string='Batch')
    rider_id = fields.Many2one('res.partner', string='Rider')
    date_received = fields.Datetime()
    date_delivered = fields.Datetime()

    _sql_constraints = [
        ('tracking_unique', 'unique(name)', 'Tracking ID must be unique!')
    ]

    @api.model
    def create_from_scan(self, tracking_id, batch=None):
        """Helper used by barcode controller: creates or updates record from scanning a tracking ID."""
        package = self.search([('name','=',tracking_id)], limit=1)
        vals = {'name': tracking_id}
        if batch:
            vals['batch_id'] = batch.id
        if not package:
            package = self.create(vals)
        else:
            package.write(vals)
        # Trigger a Dellyman sync (placeholder)
        try:
            package._sync_from_dellyman()
        except Exception:
            # swallow for now; real code should log
            pass
        return package

    def _sync_from_dellyman(self):
        """Placeholder to call connector and update the record.
        Replace with real connector calls once API doc is available.
        """
        connector = self.env['dellyman.connector']
        for rec in self:
            data = connector.fetch_package_by_tracking(rec.name)
            if not data:
                continue
            rec.write({
                'ord_id': data.get('ord_id') or data.get('order_id'),
                'package_description': data.get('description') or data.get('package_description'),
                'customer_name': data.get('customer', {}).get('name') if data.get('customer') else data.get('customer_name'),
                'customer_phone': data.get('customer', {}).get('phone') if data.get('customer') else data.get('customer_phone'),
                'customer_address': data.get('customer', {}).get('address') if data.get('customer') else data.get('customer_address'),
                'current_status': data.get('status') or rec.current_status,
            })
