from odoo import http
from odoo.http import request

class PortalPayslipDMS(http.Controller):

    def _user_email(self, user):
        return (user.email or '').strip().lower()

    @http.route('/my/payslips', type='http', auth='user', website=True)
    def portal_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        user_email = self._user_email(user)
        if not user_email:
            return request.render('mattobell_payslip_dms_auto.portal_no_employee')

        # match employee by work_email (case-insensitive)
        emp = request.env['hr.employee'].sudo().search([('work_email','ilike', user_email)], limit=1)
        if not emp:
            return request.render('mattobell_payslip_dms_auto.portal_no_employee')

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
        # find documents or attachments for slips
        doc_model = request.env['documents.document'].sudo()
        attachments = {}
        for s in slips:
            d = False
            try:
                if s.dms_document_id:
                    d = s.dms_document_id
                else:
                    # find any document referencing this payslip
                    d = doc_model.search([('attachment_id.res_model','=','hr.payslip'), ('attachment_id.res_id','=', s.id)], limit=1)
            except Exception:
                d = False
            attachments[s.id] = d
        return request.render('mattobell_payslip_dms_auto.portal_payslips_page', {
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
        # find document or attachment
        d = False
        try:
            if slip.dms_document_id:
                d = slip.dms_document_id
            else:
                d = request.env['documents.document'].sudo().search([('attachment_id.res_model','=','hr.payslip'), ('attachment_id.res_id','=', slip.id)], limit=1)
        except Exception:
            d = False
        if not d:
            return request.render('mattobell_payslip_dms_auto.portal_access_denied')
        attach = d.attachment_id if hasattr(d, 'attachment_id') else False
        if not attach:
            return request.render('mattobell_payslip_dms_auto.portal_access_denied')
        return request.redirect('/web/content/%s?download=1' % attach.id)
