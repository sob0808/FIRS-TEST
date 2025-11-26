
from odoo import http
from odoo.http import request

class PayslipPortal(http.Controller):

    @http.route(['/my/payslips'], type='http', auth='user', website=True)
    def my_payslips(self, **kw):
        user=request.env.user
        emp=request.env['hr.employee'].sudo().search([('user_id','=',user.id)],limit=1)
        if not emp:
            return request.render('portal_payslip_fixed_final.portal_no_employee')
        slips=request.env['hr.payslip'].sudo().search([('employee_id','=',emp.id)], order='date_from desc')
        return request.render('portal_payslip_fixed_final.portal_my_payslips',{
            'payslips':slips,
        })
