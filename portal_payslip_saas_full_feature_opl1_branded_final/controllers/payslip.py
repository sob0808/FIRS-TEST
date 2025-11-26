
from odoo import http
from odoo.http import request
import base64, io

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE=True
except:
    PYPDF2_AVAILABLE=False

class PayslipPortal(http.Controller):

    @http.route(['/my/payslips'], type='http', auth='user', website=True)
    def my(self, month=None, year=None, **kw):
        user=request.env.user
        emp=request.env['hr.employee'].sudo().search([('user_id','=',user.id)], limit=1)
        if not emp:
            return request.render('portal_payslip_saas_full_feature_opl1_branded_final.portal_no_employee')

        domain=[('employee_id','=',emp.id)]
        if month and year:
            try:
                m=int(month); y=int(year)
                domain += [('date_from','>=', f"{y}-{m:02d}-01"), ('date_to','<=', f"{y}-{m:02d}-31")]
            except:
                pass
        elif year:
            try:
                y=int(year)
                domain += [('date_from','>=', f"{y}-01-01"), ('date_to','<=', f"{y}-12-31")]
            except:
                pass

        slips=request.env['hr.payslip'].sudo().search(domain, order="date_from desc")
        Att=request.env['ir.attachment'].sudo()
        attachments={s.id:Att.search([('res_model','=','hr.payslip'),('res_id','=',s.id)]) for s in slips}

        return request.render('portal_payslip_saas_full_feature_opl1_branded_final.portal_my_payslips_page',{
            'payslips':slips,
            'attachments':attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
            'total_payslips': len(slips),
            'last_period': slips[0].date_from if slips else None
        })

    @http.route(['/my/payslips/<int:pid>/download'], type='http', auth='user', website=True)
    def dl(self,pid,watermark='1',**kw):
        slip=request.env['hr.payslip'].sudo().browse(pid)
        if not slip or slip.employee_id.user_id.id!=request.uid:
            return request.not_found()
        pdf=request.env.ref('hr_payroll.report_payslip')._render_qweb_pdf([slip.id])[0]

        Settings=request.env['portal.payslip.settings'].sudo().search([],limit=1)
        if Settings and PYPDF2_AVAILABLE and watermark=='1':
            overlay=Settings.watermark_attachment or Settings.signature_attachment
            if overlay:
                try:
                    reader=PdfReader(io.BytesIO(pdf))
                    writer=PdfWriter()
                    o_pdf=base64.b64decode(overlay.datas)
                    o_reader=PdfReader(io.BytesIO(o_pdf))
                    for p in reader.pages:
                        try: p.merge_page(o_reader.pages[0])
                        except: pass
                        writer.add_page(p)
                    buf=io.BytesIO()
                    writer.write(buf)
                    pdf=buf.getvalue()
                except:
                    pass

        return request.make_response(pdf,[
            ('Content-Type','application/pdf'),
            ('Content-Disposition',f'attachment; filename=payslip_{slip.number or slip.id}.pdf')
        ])
