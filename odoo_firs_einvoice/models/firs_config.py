from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class FirsConfig(models.TransientModel):
    _inherit = "res.config.settings"

    firs_api_url = fields.Char("FIRS API URL", default="https://api.taxpromax.com/einvoice/v1")
    firs_api_username = fields.Char("FIRS API Username")
    firs_api_password = fields.Char("FIRS API Password")
    firs_tin = fields.Char("Company TIN")
    firs_environment = fields.Selection([('sandbox','Sandbox'),('prod','Production')], default='prod')

    # New fields for modern FIRS portal
    firs_entry_id = fields.Char("FIRS Entry ID")
    firs_business_id = fields.Char("FIRS Business ID")
    firs_api_key = fields.Char("FIRS API Key")
    firs_client_secret = fields.Char("FIRS Client Secret")
    firs_irn_template = fields.Char("IRN Template")

    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update({
            'firs_api_url': ICP.get_param('firs.api_url') or '',
            'firs_api_username': ICP.get_param('firs.api_username') or '',
            'firs_api_password': ICP.get_param('firs.api_password') or '',
            'firs_tin': ICP.get_param('firs.tin') or '',
            'firs_environment': ICP.get_param('firs.environment') or 'prod',
            'firs_entry_id': ICP.get_param('firs.entry_id') or '',
            'firs_business_id': ICP.get_param('firs.business_id') or '',
            'firs_api_key': ICP.get_param('firs.api_key') or '',
            'firs_client_secret': ICP.get_param('firs.client_secret') or '',
            'firs_irn_template': ICP.get_param('firs.irn_template') or '',
        })
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('firs.api_url', self.firs_api_url or '')
        ICP.set_param('firs.api_username', self.firs_api_username or '')
        ICP.set_param('firs.api_password', self.firs_api_password or '')
        ICP.set_param('firs.tin', self.firs_tin or '')
        ICP.set_param('firs.environment', self.firs_environment or 'prod')
        ICP.set_param('firs.entry_id', self.firs_entry_id or '')
        ICP.set_param('firs.business_id', self.firs_business_id or '')
        ICP.set_param('firs.api_key', self.firs_api_key or '')
        ICP.set_param('firs.client_secret', self.firs_client_secret or '')
        ICP.set_param('firs.irn_template', self.firs_irn_template or '')

    def action_test_connection(self):
        """Test FIRS connection using API Key / Client Secret headers if provided."""
        ICP = self.env['ir.config_parameter'].sudo()
        url = ICP.get_param('firs.api_url')
        api_key = ICP.get_param('firs.api_key')
        client_secret = ICP.get_param('firs.client_secret')
        entry_id = ICP.get_param('firs.entry_id')
        business_id = ICP.get_param('firs.business_id')
        if not url:
            return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'FIRS Connection', 'message': 'FIRS API URL not configured.', 'type': 'warning', 'sticky': False } }
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['X-API-KEY'] = api_key
        if client_secret:
            headers['X-CLIENT-SECRET'] = client_secret
        if entry_id:
            headers['X-ENTRY-ID'] = entry_id
        if business_id:
            headers['X-BUSINESS-ID'] = business_id
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            status = resp.status_code
            if 200 <= status < 300:
                return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'FIRS Connection', 'message': f'✅ Connection successful (HTTP {status}).', 'type': 'success', 'sticky': False } }
            else:
                _logger.warning('FIRS ping returned non-2xx: %s %s', status, resp.text[:1000])
                return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'FIRS Connection', 'message': f'❌ Connection failed (HTTP {status}). See logs.', 'type': 'danger', 'sticky': True } }
        except Exception as e:
            _logger.exception('FIRS connection test error: %s', e)
            return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {'title': 'FIRS Connection', 'message': f'❌ Connection error: {e}', 'type': 'danger', 'sticky': True } }

