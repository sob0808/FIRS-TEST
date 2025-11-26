from odoo import http
from odoo.http import request
import base64, io

class PayslipPortal(http.Controller):

    @http.route(['/my/payslips'], type='http', auth='user', website=True)
    def my_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id','=', user.id)], limit=1)
        if not employee:
            return request.render('portal_payslip_corrected.portal_no_employee')

        domain=[('employee_id','=',employee.id)]
        if month and year:
            try:
                m=int(month); y=int(year)
                domain += [('date_from','>=',f"{y}-{m:02d}-01"),('date_to','<=',f"{y}-{m:02d}-31")]
            except:
                pass
        elif year:
            try:
                y=int(year)
                domain += [('date_from','>=',f"{y}-01-01"),('date_to','<=',f"{y}-12-31")]
            except:
                pass

        slips=request.env['hr.payslip'].sudo().search(domain, order='date_from desc')
        Att=request.env['ir.attachment'].sudo()
        attachments={s.id: Att.search([('res_model','=','hr.payslip'),('res_id','=',s.id)]) for s in slips}

        return request.render('portal_payslip_corrected.portal_my_payslips_page',{
            'payslips':slips,
            'attachments':attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
            'total_payslips': len(slips),
        })
