from odoo import models, fields
import base64, qrcode, json
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    firs_irn = fields.Char("FIRS IRN", copy=False)
    firs_status = fields.Selection([('none','Not Submitted'),('pending','Pending'),('validated','Validated'),('error','Error')], default='none', copy=False)
    firs_response = fields.Text("FIRS Response", copy=False)
    firs_qr = fields.Binary("FIRS QR Code", copy=False)

    def _firs_build_payload(self):
        self.ensure_one()
        lines = []
        for l in self.invoice_line_ids:
            lines.append({
                'description': l.name,
                'quantity': float(l.quantity),
                'unitPrice': float(l.price_unit),
                'taxRate': sum(tax.amount for tax in l.tax_ids),
                'total': float(l.price_subtotal),
            })
        payload = {
            'invoiceNumber': self.name,
            'sellerTIN': self.company_id.vat or self.env['ir.config_parameter'].sudo().get_param('firs.tin'),
            'buyerName': self.partner_id.name,
            'buyerTIN': self.partner_id.vat or '',
            'invoiceDate': str(self.invoice_date),
            'invoiceTotal': float(self.amount_total),
            'lines': lines,
        }
        return payload

    def _set_qr_from_text(self, text: str):
        img = qrcode.make(text)
        buf = BytesIO()
        img.save(buf, format='PNG')
        self.firs_qr = base64.b64encode(buf.getvalue())

    def action_firs_send(self):
        for move in self:
            if move.move_type != 'out_invoice':
                continue
            move.write({'firs_status': 'pending'})
            payload = move._firs_build_payload()
            # send via client
            res = self.env['firs.client'].send_invoice(payload)
            if res.get('success'):
                data = res.get('data') or {}
                irn = data.get('irn') or data.get('invoiceReference')
                qr_text = data.get('qr') or irn

                move.write({'firs_response': json.dumps(data) if isinstance(data, dict) else str(data)})
                if irn:
                    move.write({'firs_irn': irn, 'firs_status': 'validated'})
                    if qr_text:
                        if isinstance(qr_text, str) and qr_text.strip().startswith('iVBOR'):
                            move.write({'firs_qr': qr_text})
                        else:
                            move._set_qr_from_text(qr_text)
                else:
                    move.write({'firs_status': 'error'})
            else:
                move.write({'firs_status': 'error', 'firs_response': res.get('error')})
        return True

    def action_post(self):
        res = super().action_post()
        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            try:
                move.action_firs_send()
            except Exception as e:
                move.message_post(body=f'FIRS submission exception: {e}')
                move.write({'firs_status': 'error', 'firs_response': str(e)})
        return res
