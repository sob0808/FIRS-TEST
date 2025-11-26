from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class PortalPayslips(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        payslip_count = request.env['hr.payslip'].search_count([
            ('employee_id.user_id', '=', request.uid)
        ])
        values['payslip_count'] = payslip_count
        return values

    @http.route(['/my/payslips'], type='http', auth='portal', website=True)
    def portal_my_payslips(self, **kw):
        payslips = request.env['hr.payslip'].search([
            ('employee_id.user_id', '=', request.uid)
        ])
        return request.render('portal_payslip_access.portal_my_payslips_page', {
            'payslips': payslips,
        })

    @http.route(['/my/payslips/<int:payslip_id>/download'], type='http', auth='portal', website=True)
    def download_payslip(self, payslip_id=None, **kw):
        payslip = request.env['hr.payslip'].sudo().browse(payslip_id)
        if payslip.employee_id.user_id.id != request.uid:
            return request.not_found()

        pdf = request.env.ref('hr_payroll.report_payslip')._render_qweb_pdf([payslip.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', f'attachment; filename=payslip_{payslip.number}.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
