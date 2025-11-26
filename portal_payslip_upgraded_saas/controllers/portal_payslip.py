from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import io

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False

class PortalPayslips(CustomerPortal):

    @http.route(['/my/payslips'], type='http', auth='portal', website=True)
    def portal_my_payslips(self, month=None, year=None, **kw):
        domain = [('employee_id.user_id', '=', request.uid)]

        if month and year:
            try:
                m = int(month); y = int(year)
                start = f"{y}-{m:02d}-01"
                end = f"{y}-{m:02d}-31"
                domain += [('date_from', '>=', start), ('date_to', '<=', end)]
            except Exception:
                pass
        elif year:
            try:
                y = int(year)
                domain += [('date_from', '>=', f"{y}-01-01"), ('date_to', '<=', f"{y}-12-31")]
            except Exception:
                pass

        payslips = request.env['hr.payslip'].search(domain, order='date_from desc')

        # Attachments grouped by payslip
        attachments = {}
        Att = request.env['ir.attachment']
        for slip in payslips:
            attachments[slip.id] = Att.search([('res_model', '=', 'hr.payslip'), ('res_id', '=', slip.id)])

        total_payslips = len(payslips)
        last_period = payslips[:1].date_from if payslips else None

        return request.render('portal_payslip_upgraded_saas.portal_my_payslips_page', {
            'payslips': payslips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
            'total_payslips': total_payslips,
            'last_period': last_period,
        })

    @http.route(['/my/payslips/<int:payslip_id>/download'], type='http', auth='portal', website=True)
    def download_payslip(self, payslip_id=None, watermark='1', **kw):
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        if payslip.employee_id.user_id.id != request.uid:
            return request.not_found()

        try:
            report = request.env.ref('hr_payroll.report_payslip')
            pdf = report._render_qweb_pdf([payslip.id])[0]
        except Exception:
            return request.not_found()

        # Fetch SaaS-optimized settings record (custom model)
        Settings = request.env['portal.payslip.settings'].sudo()
        settings = Settings.search([], limit=1)

        sig_att = settings.signature_attachment if settings else False
        wm_att = settings.watermark_attachment if settings else False

        if PYPDF2_AVAILABLE and (sig_att or wm_att) and watermark == '1':
            try:
                reader = PdfReader(io.BytesIO(pdf))
                writer = PdfWriter()
                overlay_att = wm_att or sig_att
                if overlay_att and overlay_att.datas:
                    overlay_pdf = base64.b64decode(overlay_att.datas)
                    overlay_reader = PdfReader(io.BytesIO(overlay_pdf))
                    for p in reader.pages:
                        new_page = p
                        try:
                            overlay_page = overlay_reader.pages[0]
                            new_page.merge_page(overlay_page)
                        except Exception:
                            pass
                        writer.add_page(new_page)
                    out = io.BytesIO()
                    writer.write(out)
                    pdf = out.getvalue()
            except Exception:
                pass

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', f'attachment; filename=payslip_{payslip.number or payslip.id}.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
