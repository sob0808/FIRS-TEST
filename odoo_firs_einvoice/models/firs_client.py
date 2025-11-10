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
            'endpoint': ICP.get_param('firs.api_endpoint', default='/api/v1/invoice/sign'),
            'username': ICP.get_param('firs.api_username'),
            'password': ICP.get_param('firs.api_password'),
            'tin': ICP.get_param('firs.tin'),
            'entry_id': ICP.get_param('firs.entry_id'),
            'business_id': ICP.get_param('firs.business_id'),
            'api_key': ICP.get_param('firs.api_key'),
            'client_secret': ICP.get_param('firs.client_secret'),
            'irn_template': ICP.get_param('firs.irn_template'),
        }

    def _get_endpoint_url(self, base_url: str, endpoint_path: str) -> str:
        """
        Construct the full endpoint URL for invoice submission.
        
        Uses the configured endpoint path from settings.
        Handles case where base URL ends with /api and endpoint starts with /api.
        
        Args:
            base_url: Base API URL (e.g., https://eivc-k6z6d.ondigitalocean.app/api)
            endpoint_path: Configured endpoint path (e.g., /api/v1/invoice/sign)
        """
        if not base_url:
            return base_url
        
        # Remove trailing slash if present
        base_url = base_url.rstrip('/')
        
        # If endpoint_path is configured, use it
        if endpoint_path:
            endpoint_path = endpoint_path.strip()
            # Ensure it starts with /
            if not endpoint_path.startswith('/'):
                endpoint_path = '/' + endpoint_path
            
            # Handle duplicate /api in path
            # If base_url ends with /api and endpoint_path starts with /api, remove /api from endpoint_path
            if base_url.endswith('/api') and endpoint_path.startswith('/api'):
                endpoint_path = endpoint_path[4:]  # Remove '/api' from start
                _logger.info('Removed duplicate /api from endpoint path')
            
            endpoint = base_url + endpoint_path
            _logger.info('Using configured endpoint path: %s + %s = %s', base_url, endpoint_path, endpoint)
            return endpoint
        
        # Fallback: If URL already contains what looks like a submission endpoint, use as-is
        if any(path in base_url for path in ['/einvoice/post', '/einvoice/submit', '/submit', '/post']):
            _logger.info('Using configured URL as-is (appears to be full endpoint): %s', base_url)
            return base_url
        
        # Fallback: If URL ends with /api, append /einvoice/post
        if base_url.endswith('/api'):
            endpoint = base_url + '/einvoice/post'
            _logger.warning('No endpoint path configured. Using fallback: %s -> %s. Please configure endpoint path in settings!', base_url, endpoint)
            return endpoint
        
        # Fallback: If URL ends with /api/v1, append /einvoice/post
        if base_url.endswith('/api/v1'):
            endpoint = base_url + '/einvoice/post'
            _logger.warning('No endpoint path configured. Using fallback: %s -> %s. Please configure endpoint path in settings!', base_url, endpoint)
            return endpoint
        
        # Fallback: If URL ends with /einvoice/v1, might need /submit or /post
        if base_url.endswith('/einvoice/v1'):
            endpoint = base_url + '/post'
            _logger.warning('No endpoint path configured. Using fallback: %s -> %s. Please configure endpoint path in settings!', base_url, endpoint)
            return endpoint
        
        # Default fallback
        endpoint = base_url + '/einvoice/post'
        _logger.warning('No endpoint path configured. Using default fallback: %s -> %s. Please configure endpoint path in settings based on API docs!', base_url, endpoint)
        return endpoint

    def _build_headers(self, conf: dict):
        headers = {'Content-Type': 'application/json'}
        api_key = conf.get('api_key')
        if api_key:
            headers['x-api-key'] = str(api_key)
        api_secret = conf.get('client_secret')  # client_secret is stored as api_secret
        if api_secret:
            headers['x-api-secret'] = str(api_secret)
        entry_id = conf.get('entry_id')
        if entry_id:
            headers['x-entry-id'] = str(entry_id)
        business_id = conf.get('business_id')
        if business_id:
            headers['x-business-id'] = str(business_id)
        return headers

    def _make_request(self, method: str, endpoint_path: str, payload: dict | None = None) -> dict:
        """Make a request to the FIRS API"""
        conf = self._get_conf()
        base_url = conf.get('url')
        if not base_url:
            return {'success': False, 'error': 'FIRS API URL not configured'}
        
        url = self._get_endpoint_url(base_url, endpoint_path)
        _logger.info('FIRS API %s request to: %s', method, url)
        
        headers = self._build_headers(conf)
        
        # Build curl command for debugging
        def _build_curl_command(method, url, headers, payload):
            """Build a curl command string for debugging"""
            import json
            import shlex
            
            curl_lines = [f'curl -X {method.upper()} {shlex.quote(url)}']
            
            # Add headers
            for key, value in headers.items():
                curl_lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
            
            # Add payload for POST/PUT requests
            if payload and method.upper() in ('POST', 'PUT', 'PATCH'):
                payload_json = json.dumps(payload, indent=2)
                # Use --data-raw for better formatting
                curl_lines.append(f"  --data-raw {shlex.quote(payload_json)}")
            
            return ' \\\n'.join(curl_lines)
        
        try:
            if method.upper() == 'GET':
                resp = requests.get(url, headers=headers, timeout=30)
            else:
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
            
            resp.raise_for_status()
            data = resp.json() if 'application/json' in resp.headers.get('Content-Type','') else {'raw': resp.text}
            _logger.info('FIRS response: %s', data)
            return {'success': True, 'data': data}
        except requests.exceptions.HTTPError as e:
            # Log complete curl command for debugging
            curl_cmd = _build_curl_command(method, url, headers, payload)
            _logger.error('=' * 80)
            _logger.error('FIRS API HTTP Error: %s', e)
            _logger.error('URL: %s', url)
            _logger.error('Method: %s', method.upper())
            _logger.error('Status Code: %s', e.response.status_code if hasattr(e, 'response') else 'N/A')
            _logger.error('')
            _logger.error('CURL COMMAND TO REPRODUCE:')
            _logger.error('-' * 80)
            _logger.error(curl_cmd)
            _logger.error('-' * 80)
            _logger.error('')
            
            # Log response details
            if hasattr(e, 'response'):
                _logger.error('Response Headers: %s', dict(e.response.headers))
                _logger.error('Response Body: %s', e.response.text[:2000])
            
            _logger.error('=' * 80)
            
            error_msg = str(e)
            if hasattr(e.response, 'text'):
                error_msg += f" - Response: {e.response.text[:500]}"
            return {'success': False, 'error': error_msg}
        except Exception as e:
            # Log complete curl command even for non-HTTP errors
            curl_cmd = _build_curl_command(method, url, headers, payload)
            _logger.error('=' * 80)
            _logger.error('FIRS API Error: %s', e)
            _logger.error('URL: %s', url)
            _logger.error('Method: %s', method.upper())
            _logger.error('')
            _logger.error('CURL COMMAND TO REPRODUCE:')
            _logger.error('-' * 80)
            _logger.error(curl_cmd)
            _logger.error('-' * 80)
            _logger.error('=' * 80)
            return {'success': False, 'error': str(e)}

    def validate_invoice(self, payload: dict) -> dict:
        """Validate invoice data before signing"""
        return self._make_request('POST', '/api/v1/invoice/validate', payload)

    def sign_invoice(self, payload: dict) -> dict:
        """Sign/submit invoice to FIRS"""
        conf = self._get_conf()
        endpoint_path = conf.get('endpoint', '/api/v1/invoice/sign')
        return self._make_request('POST', endpoint_path, payload)

    def confirm_invoice(self, irn: str) -> dict:
        """Confirm invoice status by IRN"""
        return self._make_request('GET', f'/api/v1/invoice/confirm/{irn}')

    def validate_irn(self, invoice_reference: str, business_id: str, irn: str) -> dict:
        """Validate an IRN"""
        payload = {
            'invoice_reference': invoice_reference,
            'business_id': business_id,
            'irn': irn
        }
        return self._make_request('POST', '/api/v1/invoice/irn/validate', payload)

    def send_invoice(self, payload: dict) -> dict:
        """Legacy method - now calls sign_invoice"""
        return self.sign_invoice(payload)
