from odoo import http
from odoo.http import request

class PortalPayslipController(http.Controller):

    @http.route('/my/payslips', type='http', auth='user', website=True)
    def portal_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id','=', user.id)], limit=1)
        if not emp:
            return request.render('mattobell_portal_payslip.portal_no_employee')

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

        return request.render('mattobell_portal_payslip.portal_payslips_page', {
            'employee': emp,
            'payslips': slips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
        })

    @http.route('/my/payslips/<int:pid>/download', type='http', auth='user', website=True)
    def portal_payslip_download(self, pid, watermark='1', **kw):
        slip = request.env['hr.payslip'].sudo().browse(pid)
        # allow only employee owner
        if not slip.exists() or (slip.employee_id.user_id and slip.employee_id.user_id.id != request.uid):
            # also allow if employee.work_email matches user.email (hybrid match)
            emp = slip.employee_id
            if not (emp and emp.work_email and emp.work_email.strip().lower() == (request.env.user.email or '').strip().lower()):
                return request.not_found()

        # try custom mattobell report first, fallback to default if available
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
