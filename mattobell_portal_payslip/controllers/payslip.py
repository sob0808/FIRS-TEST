from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class PortalPayslipController(http.Controller):

    @http.route('/my/payslips', type='http', auth='user', website=True)
    def portal_payslips(self, month=None, year=None, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        if not emp:
            return request.render('mattobell_portal_payslip.portal_no_employee')

        domain = [('employee_id', '=', emp.id)]
        if month and year:
            try:
                m = int(month);
                y = int(year)
                domain += [('date_from', '>=', f"{y}-{m:02d}-01"), ('date_to', '<=', f"{y}-{m:02d}-31")]
            except:
                pass
        elif year:
            try:
                y = int(year)
                domain += [('date_from', '>=', f"{y}-01-01"), ('date_to', '<=', f"{y}-12-31")]
            except:
                pass

        slips = request.env['hr.payslip'].sudo().search(domain, order='date_from desc')
        Att = request.env['ir.attachment'].sudo()
        attachments = {s.id: Att.search([('res_model', '=', 'hr.payslip'), ('res_id', '=', s.id)]) for s in slips}

        return request.render('mattobell_portal_payslip.portal_payslips_page', {
            'employee': emp,
            'payslips': slips,
            'attachments': attachments,
            'selected_month': int(month) if month else None,
            'selected_year': int(year) if year else None,
        })

    @http.route('/my/payslips/<int:pid>/download', type='http', auth='user', website=True)
    def portal_payslip_download(self, pid, watermark='1', **kw):
        """Download payslip PDF for authenticated user"""
        try:
            # Get the payslip with sudo to check if it exists
            slip = request.env['hr.payslip'].sudo().browse(pid)

            if not slip.exists():
                _logger.warning(f"Payslip {pid} does not exist")
                return request.not_found()

            # Verify user has access to this payslip
            user = request.env.user
            emp = slip.employee_id

            # Check if user owns this payslip through employee record
            has_access = False

            # Method 1: Direct user_id link
            if emp.user_id and emp.user_id.id == user.id:
                has_access = True

            # Method 2: Email match (case-insensitive)
            elif emp.work_email and user.email:
                if emp.work_email.strip().lower() == user.email.strip().lower():
                    has_access = True

            if not has_access:
                _logger.warning(
                    f"User {user.id} ({user.email}) tried to access payslip {pid} for employee {emp.id} ({emp.work_email})")
                return request.not_found()

            # Try to get the custom report first
            report = None
            report_name = None

            try:
                report = request.env.ref('mattobell_custom_payslip_pdf.mattobell_custom_payslip_pdf',
                                         raise_if_not_found=False)
                if report:
                    report_name = 'mattobell_custom_payslip_pdf'
                    _logger.info(f"Using custom report: {report_name}")
            except Exception as e:
                _logger.warning(f"Custom report not found: {e}")

            # Fallback to default Odoo payslip report
            if not report:
                try:
                    report = request.env.ref('hr_payroll.action_report_payslip', raise_if_not_found=False)
                    if report:
                        report_name = 'hr_payroll.action_report_payslip'
                        _logger.info(f"Using default report: {report_name}")
                except Exception as e:
                    _logger.warning(f"Default report not found: {e}")

            # Last resort - try to find any payslip report
            if not report:
                report = request.env['ir.actions.report'].sudo().search([
                    ('model', '=', 'hr.payslip'),
                    ('report_type', '=', 'qweb-pdf')
                ], limit=1)
                if report:
                    report_name = report.report_name
                    _logger.info(f"Using fallback report: {report_name}")

            if not report:
                _logger.error("No payslip report found in system")
                return request.make_response(
                    "No payslip report configured in system. Please contact administrator.",
                    status=500
                )

            # Generate the PDF
            try:
                pdf_content, _ = report.sudo()._render_qweb_pdf(report.id, [slip.id])

                # Prepare filename
                filename = f"payslip_{slip.number or slip.id}.pdf"

                _logger.info(f"Successfully generated PDF for payslip {pid}, size: {len(pdf_content)} bytes")

                return request.make_response(
                    pdf_content,
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', f'attachment; filename={filename}'),
                        ('Content-Length', len(pdf_content))
                    ]
                )

            except Exception as e:
                _logger.error(f"Error rendering PDF for payslip {pid}: {str(e)}", exc_info=True)
                return request.make_response(
                    f"Error generating PDF: {str(e)}",
                    status=500
                )

        except Exception as e:
            _logger.error(f"Unexpected error in payslip download: {str(e)}", exc_info=True)
            return request.make_response(
                "An unexpected error occurred. Please contact administrator.",
                status=500
            )