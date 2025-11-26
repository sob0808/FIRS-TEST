from odoo import http
from odoo.http import request
import base64, io
try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False

class MattobellPayslipPortal(http.Controller):

    @http.route(['/my/payslips'], type='http', auth='user', website=True)
    def my_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id','=', user.id)], limit=1)
        if not employee:
            return request.render('mattobell_portal_payslip.portal_no_employee')

        domain = [('employee_id','=', employee.id)]
        if month and year:
            try:
                m = int(month); y = int(year)
                domain += [('date_from','>=', f"{y}-{m:02d}-01"), ('date_to','<=', f"{y}-{m:02d}-31")]
            except Exception:
                pass
        elif year:
            try:
                y = int(year)
                domain += [('date_from','>=', f"{y}-01-01"), ('date_to','<=', f"{y}-12-31")]
            except Exception:
                pass

        payslips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc')
        Att = request.env['ir.attachment'].sudo()
        attachments = {slip.id: Att.search([('res_model','=','hr.payslip'), ('res_id','=', slip.id)]) for slip in payslips}
        return request.render('mattobell_portal_payslip.portal_my_payslips_page', {
            'payslips': payslips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
            'total_payslips': len(payslips),
            'last_period': payslips[:1].date_from if payslips else None,
        })

    @http.route(['/my/payslips/<int:payslip_id>/download'], type='http', auth='user', website=True)
    def download_payslip(self, payslip_id, watermark='1', **kw):
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        if not payslip.exists() or (payslip.employee_id.user_id and payslip.employee_id.user_id.id != request.uid):
            return request.not_found()

        try:
            report = request.env.ref('hr_payroll.report_payslip')
            pdf = report._render_qweb_pdf([payslip.id])[0]
        except Exception:
            return request.not_found()

        Settings = request.env['portal.payslip.settings'].sudo()
        settings = Settings.search([], limit=1)
        sig = settings.signature_attachment if settings else False
        wm = settings.watermark_attachment if settings else False

        if PYPDF2_AVAILABLE and (sig or wm) and watermark == '1':
            try:
                reader = PdfReader(io.BytesIO(pdf))
                writer = PdfWriter()
                overlay_att = wm or sig
                if overlay_att and overlay_att.datas:
                    overlay_pdf = base64.b64decode(overlay_att.datas)
                    overlay_reader = PdfReader(io.BytesIO(overlay_pdf))
                    for p in reader.pages:
                        try:
                            p.merge_page(overlay_reader.pages[0])
                        except Exception:
                            pass
                        writer.add_page(p)
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
