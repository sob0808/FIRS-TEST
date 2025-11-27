from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class DellymanConnector(models.AbstractModel):
    _name = 'dellyman.connector'
    _description = 'Connector to Dellyman API (placeholder)'

    api_base = fields.Char(string='Dellyman API Base', default='https://api.dellyman.example')
    api_key = fields.Char(string='API Key')

    def _get_auth_headers(self):
        key = self.api_key or self.env['ir.config_parameter'].sudo().get_param('dellyman.api_key')
        if key:
            return {'Authorization': f'Bearer {key}'}
        return {}

    def fetch_package_by_tracking(self, tracking_id):
        """Stub: fetch a package's details using tracking ID.
        Replace the URL and parsing with real API response mapping when available.
        """
        _logger.info('Fetching Dellyman package for tracking_id=%s', tracking_id)
        # TODO: implement real HTTP call
        return None

    def fetch_status(self, tracking_id):
        data = self.fetch_package_by_tracking(tracking_id)
        if data:
            return data.get('status')
        return None
