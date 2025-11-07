import requests, logging
from odoo import models

_logger = logging.getLogger(__name__)

class FirsClient(models.AbstractModel):
    _name = 'firs.client'
    _description = 'FIRS e-Invoice API Client'

    def _get_conf(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'url': ICP.get_param('firs.api_url'),
            'username': ICP.get_param('firs.api_username'),
            'password': ICP.get_param('firs.api_password'),
            'tin': ICP.get_param('firs.tin'),
            'entry_id': ICP.get_param('firs.entry_id'),
            'business_id': ICP.get_param('firs.business_id'),
            'api_key': ICP.get_param('firs.api_key'),
            'client_secret': ICP.get_param('firs.client_secret'),
            'irn_template': ICP.get_param('firs.irn_template'),
        }

    def _build_headers(self, conf: dict):
        headers = {'Content-Type': 'application/json'}
        if conf.get('api_key'):
            headers['X-API-KEY'] = conf.get('api_key')
        if conf.get('client_secret'):
            headers['X-CLIENT-SECRET'] = conf.get('client_secret')
        if conf.get('entry_id'):
            headers['X-ENTRY-ID'] = conf.get('entry_id')
        if conf.get('business_id'):
            headers['X-BUSINESS-ID'] = conf.get('business_id')
        return headers

    def send_invoice(self, payload: dict) -> dict:
        conf = self._get_conf()
        url = conf.get('url')
        if not url:
            return {'success': False, 'error': 'FIRS API URL not configured'}
        headers = self._build_headers(conf)
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json() if 'application/json' in resp.headers.get('Content-Type','') else {'raw': resp.text}
            _logger.info('FIRS response: %s', data)
            return {'success': True, 'data': data}
        except Exception as e:
            _logger.exception('FIRS API error: %s', e)
            return {'success': False, 'error': str(e)}
