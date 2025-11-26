from odoo import http
from odoo.http import request

class PortalPayslipEmailMatch(http.Controller):
    """Portal payslip controller: lists and allows download when employee.work_email == user.email"""

    def _user_email(self, user):
        return (user.email or '').strip().lower()

    @http.route('/my/payslips', type='http', auth='user', website=True)
    def portal_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        user_email = self._user_email(user)
        if not user_email:
            return request.render('mattobell_portal_payslip_emailmatch.portal_no_employee')

        # find employees with matching work_email
        emp = request.env['hr.employee'].sudo().search([('work_email','ilike', user_email)], limit=1)
        if not emp:
            return request.render('mattobell_portal_payslip_emailmatch.portal_no_employee')

        domain = [('employee_id','=', emp.id)]
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

        slips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc')
        Att = request.env['ir.attachment'].sudo()
        attachments = {s.id: Att.search([('res_model','=','hr.payslip'), ('res_id','=', s.id)]) for s in slips}

        return request.render('mattobell_portal_payslip_emailmatch.portal_payslips_page', {
            'employee': emp,
            'payslips': slips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
        })

    @http.route('/my/payslips/<int:pid>/download', type='http', auth='user', website=True)
    def portal_payslip_download(self, pid, watermark='1', **kw):
        slip = request.env['hr.payslip'].sudo().browse(pid)
        if not slip.exists():
            return request.not_found()

        user = request.env.user
        user_email = self._user_email(user)
        if not user_email:
            return request.render('mattobell_portal_payslip_emailmatch.portal_access_denied')

        emp = slip.employee_id.sudo()
        emp_email = (emp.work_email or '').strip().lower()
        if not emp_email or emp_email != user_email:
            return request.render('mattobell_portal_payslip_emailmatch.portal_access_denied')

        # choose report: prefer custom mattobell, fallback to hr_payroll
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
