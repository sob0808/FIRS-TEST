
from odoo import http
from odoo.http import request
import base64, io
try:
    from PyPDF2 import PdfReader, PdfWriter
    OK=True
except:
    OK=False

class PortalPayslip(http.Controller):

    def _allowed(self, slip):
        user=request.env.user
        emp=slip.employee_id
        if emp.user_id and emp.user_id.id==user.id:
            return True
        if emp.work_email and emp.work_email.strip().lower()==(user.email or '').strip().lower():
            return True
        return False

    @http.route('/my/payslips', auth='user', website=True)
    def list(self, **kw):
        user=request.env.user
        Emp=request.env['hr.employee'].sudo()
        emp=Emp.search(['|',('user_id','=',user.id),('work_email','ilike',user.email)], limit=1)
        if not emp:
            return request.render("mattobell_portal_payslip_smart.no_employee")

        slips=request.env['hr.payslip'].sudo().search([('employee_id','=',emp.id)], order="date_from desc")
        Att=request.env['ir.attachment'].sudo()
        atts={s.id:Att.search([('res_model','=','hr.payslip'),('res_id','=',s.id)]) for s in slips}
        return request.render("mattobell_portal_payslip_smart.page",{"payslips":slips,"atts":atts})

    @http.route('/my/payslips/<int:sid>/download', auth='user', website=True)
    def dl(self, sid, **kw):
        slip=request.env['hr.payslip'].sudo().browse(sid)
        if not slip.exists() or not self._allowed(slip):
            return request.render("mattobell_portal_payslip_smart.denied")

        rep=request.env.ref("hr_payroll.report_payslip")
        pdf=rep._render_qweb_pdf([slip.id])[0]

        headers=[('Content-Type','application/pdf'),
                 ('Content-Length',len(pdf)),
                 ('Content-Disposition',f'attachment; filename=payslip_{sid}.pdf')]
        return request.make_response(pdf, headers=headers)
