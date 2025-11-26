from odoo import http
from odoo.http import request
import base64, io

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False

class PortalPayslips(http.Controller):

    @http.route(['/my/payslips'], type='http', auth='portal', website=True)
    def portal_my_payslips(self, month=None, year=None, **kw):
        domain = [('employee_id.user_id', '=', request.uid)]

        if month and year:
            try:
                m = int(month); y = int(year)
                domain += [
                    ('date_from', '>=', f"{y}-{m:02d}-01"),
                    ('date_to', '<=',   f"{y}-{m:02d}-31")
                ]
            except:
                pass
        elif year:
            try:
                y = int(year)
                domain += [
                    ('date_from', '>=', f"{y}-01-01"),
                    ('date_to', '<=',   f"{y}-12-31")
                ]
            except:
                pass

        payslips = request.env['hr.payslip'].search(domain, order="date_from desc")

        Att = request.env['ir.attachment']
        attachments = {
            slip.id: Att.search([('res_model','=','hr.payslip'),('res_id','=', slip.id)])
            for slip in payslips
        }

        return request.render('portal_payslip_upgraded_saas_fixed.portal_my_payslips_page', {
            'payslips': payslips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
            'total_payslips': len(payslips),
            'last_period': payslips[:1].date_from if payslips else None,
        })

    @http.route(['/my/payslips/<int:payslip_id>/download'], type='http', auth='portal', website=True)
    def download_payslip(self, payslip_id, watermark='1', **kw):
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        if payslip.employee_id.user_id.id != request.uid:
            return request.not_found()

        pdf = request.env.ref('hr_payroll.report_payslip')._render_qweb_pdf([payslip.id])[0]

        Settings = request.env['portal.payslip.settings'].sudo()
        settings = Settings.search([], limit=1)

        sig = settings.signature_attachment
        wm = settings.watermark_attachment

        if PYPDF2_AVAILABLE and (sig or wm) and watermark == '1':
            try:
                reader = PdfReader(io.BytesIO(pdf))
                writer = PdfWriter()
                overlay_pdf = base64.b64decode((wm or sig).datas)
                overlay_reader = PdfReader(io.BytesIO(overlay_pdf))

                for p in reader.pages:
                    overlay_page = overlay_reader.pages[0]
                    p.merge_page(overlay_page)
                    writer.add_page(p)

                buf = io.BytesIO()
                writer.write(buf)
                pdf = buf.getvalue()
            except:
                pass

        return request.make_response(pdf, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename=payslip_{payslip.number or payslip.id}.pdf')
        ])
