from odoo import http
from odoo.http import request

class BarcodeController(http.Controller):
    @http.route(['/dellyman/scan'], type='json', auth='user', methods=['POST'], csrf=False)
    def scan_tracking(self, **post):
        tracking = post.get('tracking')
        batch_id = post.get('batch_id')
        batch = None
        if batch_id:
            batch = request.env['package.batch'].sudo().browse(int(batch_id))
        package = request.env['package.order'].sudo().create_from_scan(tracking, batch)
        return {'result': 'ok', 'id': package.id}
