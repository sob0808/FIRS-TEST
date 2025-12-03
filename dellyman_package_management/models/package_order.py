from odoo import models, fields

class PackageOrder(models.Model):
    _name = "package.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Package Order"

    name = fields.Char(required=True, tracking=True)
    ord_id = fields.Char(string='Tracking ID')
    batch_id = fields.Many2one('package.batch', string='Batch')
    location_id = fields.Many2one('package.location', string='Location')
    package_description = fields.Text()
    customer_name = fields.Char()
    customer_phone = fields.Char()
    customer_address = fields.Char()
    current_status = fields.Selection([
        ('received','Received'),
        ('assigned','Assigned'),
        ('picked','Picked'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('awaiting_return','Awaiting Return'),
        ('returned','Returned')
    ], default='received', tracking=True)

    def action_set_status(self):
        status = self.env.context.get('status')
        if not status:
            return
        for rec in self:
            old = rec.current_status
            rec.current_status = status
            rec.message_post(body=f"Status changed from {old} to {status}")


import requests
from odoo import api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

    @api.model
    def fetch_from_dellyman(self, tracking_id):
        """Fetch package info from Dellyman using Tracking ID (uses ord_id field)."""
        api_key = self.env['ir.config_parameter'].sudo().get_param('dellyman.api_key')
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'dellyman.base_url', 'https://dev.dellyman.com/api/v3.0/'
        )

        if not api_key:
            raise UserError(_('Dellyman API Key not configured. Set system parameter "dellyman.api_key".'))

        url = base_url.rstrip('/') + '/TrackPackage'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        payload = {'TrackingID': tracking_id}

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
        except Exception as e:
            _logger.exception('HTTP request to Dellyman failed: %s', e)
            raise UserError(_('Unable to reach Dellyman API: %s') % e)

        if resp.status_code != 200:
            _logger.error('Dellyman returned %%s: %%s', resp.status_code, resp.text)
            raise UserError(_('Unable to fetch package: %s') % resp.text)

        data = resp.json()
        pkg = data.get('Package') or data

        vals = {
            'ord_id': tracking_id,
            'package_description': pkg.get('PackageDescription') or pkg.get('Description'),
            'customer_name': pkg.get('DeliveryContactName') or pkg.get('CustomerName'),
            'customer_phone': pkg.get('DeliveryContactNumber') or pkg.get('CustomerPhone'),
            'customer_address': pkg.get('DeliveryGooglePlaceAddress') or pkg.get('CustomerAddress'),
            'current_status': self._map_status(pkg.get('Status') or pkg.get('status')),
        }

        order = self.search([('ord_id', '=', tracking_id)], limit=1)
        if order:
            order.write(vals)
        else:
            order = self.create(vals)

        try:
            order.message_post(body=_('Imported/Updated from Dellyman: %s') % tracking_id)
        except Exception:
            pass

        return order

    def _map_status(self, status):
        if not status:
            return 'draft'
        status = status.strip().lower()
        mapping = {
            'assigned': 'assigned',
            'package picked': 'picked',
            'picked': 'picked',
            'in transit': 'in_transit',
            'in_transit': 'in_transit',
            'delivered': 'delivered',
            'awaiting return': 'awaiting_return',
            'awaiting_return': 'awaiting_return',
            'returned': 'returned',
        }
        return mapping.get(status, 'draft')
