from odoo import http
from odoo.http import request

class WebsitePayslipController(http.Controller):

    @http.route('/payslips', type='http', auth='user', website=True)
    def payslip_list(self, month=None, year=None, **kw):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id','=', user.id)], limit=1)
        if not employee:
            return request.render('mattobell_website_payslips.no_employee')
        domain=[('employee_id','=', employee.id)]
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
        attachments = {s.id: Att.search([('res_model','=','hr.payslip'),('res_id','=',s.id)]) for s in slips}
        return request.render('mattobell_website_payslips.payslip_list_template', {
            'payslips': slips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
        })

    @http.route(['/payslips/<int:pid>/download'], type='http', auth='user', website=True)
    def download(self, pid, **kw):
        slip = request.env['hr.payslip'].sudo().browse(pid)
        if not slip or slip.employee_id.user_id.id != request.uid:
            return request.not_found()
        try:
            report = request.env.ref('hr_payroll.report_payslip')
            pdf = report._render_qweb_pdf([slip.id])[0]
        except Exception:
            return request.not_found()
        return request.make_response(pdf, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename=payslip_{slip.number or slip.id}.pdf')
        ])
