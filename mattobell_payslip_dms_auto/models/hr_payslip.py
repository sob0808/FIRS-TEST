from odoo import models, fields, api, _
import base64
import logging

_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    dms_document_id = fields.Many2one('documents.document', string='Payslip Document', copy=False)

    @api.model
    def _generate_payslip_attachment(self, slip):
        # choose report
        report = None
        try:
            report = self.env.ref('mattobell_custom_payslip_pdf.mattobell_custom_payslip_pdf')
        except Exception:
            report = None
        if not report:
            try:
                report = self.env.ref('hr_payroll.report_payslip')
            except Exception:
                report = None
        if not report:
            _logger.warning('No payslip report available to generate PDF for payslip %s', slip.id)
            return False

        try:
            pdf = report._render_qweb_pdf([slip.id])[0]
        except Exception as e:
            _logger.exception('Rendering payslip PDF failed for %s: %s', slip.id, e)
            return False

        fname = f"Payslip-{slip.number or slip.id}.pdf"
        datas = base64.b64encode(pdf)
        # create attachment
        attachment = self.env['ir.attachment'].sudo().create({
            'name': fname,
            'type': 'binary',
            'datas': datas,
            'res_model': 'hr.payslip',
            'res_id': slip.id,
            'mimetype': 'application/pdf',
        })

        # create documents.document wrapper if documents module exists
        doc = None
        try:
            doc_model = self.env['documents.document']
            doc = doc_model.sudo().create({
                'name': fname,
                'attachment_id': attachment.id,
                'folder_id': False,
            })
        except Exception:
            doc = None

        # auto-share: add the employee.user partner as collaborator on document (if doc created)
        try:
            partner = slip.employee_id.user_id.partner_id if slip.employee_id and slip.employee_id.user_id else None
            if doc and partner:
                # set partner as collaborator
                doc.sudo().write({'partner_ids': [(4, partner.id)]})
            # also post message with attachment to employee (so partner can see in chatter)
            if partner:
                slip.sudo().message_post(body=_('Payslip generated and uploaded to Documents.'),
                                         subject=_('Payslip available'),
                                         partner_ids=[(4, partner.id)],
                                         attachments=[(attachment.name, base64.b64decode(attachment.datas))])
        except Exception:
            pass

        return doc or attachment

    def write(self, vals):
        # detect transition to done and generate document
        res = super(HrPayslip, self).write(vals)
        try:
            for slip in self:
                # if state is set to done either via vals or already done
                state_set = 'state' in vals and vals.get('state') == 'done'
                if state_set or slip.state == 'done':
                    # only generate if not already present
                    if not slip.dms_document_id:
                        doc_or_attach = self._generate_payslip_attachment(slip)
                        if doc_or_attach:
                            # store reference if it's a documents.document
                            try:
                                if doc_or_attach._name == 'documents.document':
                                    slip.sudo().write({'dms_document_id': doc_or_attach.id})
                                else:
                                    # try find documents.document from attachment
                                    doc = self.env['documents.document'].sudo().search([('attachment_id','=', doc_or_attach.id)], limit=1)
                                    if doc:
                                        slip.sudo().write({'dms_document_id': doc.id})
                            except Exception:
                                pass
        except Exception as e:
            _logger.exception('Error during payslip write post-processing: %s', e)
        return res
