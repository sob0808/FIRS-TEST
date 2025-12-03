import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PackageOrder(models.Model):
    _inherit = "package.order"

    tracking_id = fields.Char(string="Tracking ID", index=True)

    @api.model
    def fetch_from_dellyman(self, tracking_id):
        api_key = self.env['ir.config_parameter'].sudo().get_param('dellyman.api_key')
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'dellyman.base_url', 'https://dev.dellyman.com/api/v3.0/'
        )

        if not api_key:
            raise UserError(_("Dellyman API Key not configured."))

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
            _logger.exception("HTTP request to Dellyman failed: %s", e)
            raise UserError(_("Unable to reach Dellyman API: %s") % e)

        if resp.status_code != 200:
            raise UserError(_("Dellyman error: %s") % resp.text)

        data = resp.json()
        pkg = data.get("Package") or data

        vals = {
            'tracking_id': tracking_id,
            'ord_id': pkg.get('OrderCode') or pkg.get("OrderID"),
            'package_description': pkg.get('PackageDescription'),
            'customer_name': pkg.get('DeliveryContactName'),
            'customer_phone': pkg.get('DeliveryContactNumber'),
            'customer_address': pkg.get('DeliveryGooglePlaceAddress'),
            'current_status': self._map_status(pkg.get('Status')),
        }

        order = self.search([('tracking_id', '=', tracking_id)], limit=1)
        if order:
            order.write(vals)
        else:
            order = self.create(vals)

        return order

    def _map_status(self, status):
        if not status:
            return 'draft'
        status = status.lower()
        mapping = {
            'assigned': 'assigned',
            'package picked': 'picked',
            'in transit': 'in_transit',
            'delivered': 'delivered',
            'awaiting return': 'awaiting_return',
            'returned': 'returned',
        }
        return mapping.get(status, 'draft')
