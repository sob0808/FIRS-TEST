from odoo import http
from odoo.http import request

class PortalPayslipRelaxed(http.Controller):
    """Relaxed download route for /my/payslips/<id>/download

    Allows download when either:
      - employee.user_id == current user
      - employee.work_email matches current user's email (case-insensitive)
    """

    @http.route('/my/payslips/<int:pid>/download', type='http', auth='user', website=True)
    def relaxed_download(self, pid, **kw):
        slip = request.env['hr.payslip'].sudo().browse(pid)
        if not slip.exists():
            return request.not_found()

        user = request.env.user
        emp = slip.employee_id.sudo()

        # relaxed matching: user_id or work_email
        ok = False

        # match by related user
        if emp.user_id and emp.user_id.id == user.id:
            ok = True

        # match by employee work email vs user email
        try:
            user_email = (user.email or '').strip().lower()
            emp_email = (emp.work_email or '').strip().lower()
            if emp_email and user_email and emp_email == user_email:
                ok = True
        except Exception:
            pass

        if not ok:
            return request.not_found()

        # find report (prefer custom mattobell report, fallback to hr_payroll)
        report = None
        try:
            report = request.env.ref('mattobell_custom_payslip_pdf.mattobell_custom_payslip_pdf')
        except Exception:
            report = None
        if not report:
            try:
                report = request.env.ref('hr_payroll.report_payslip')
            except Exception:
                report = None

        if not report:
            return request.not_found()

        try:
            pdf = report._render_qweb_pdf([slip.id])[0]
        except Exception:
            return request.not_found()

        return request.make_response(pdf, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename=payslip_{slip.number or slip.id}.pdf')
        ])
