import logging

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FirsConfig(models.TransientModel):
    _inherit = "res.config.settings"

    firs_enabled = fields.Boolean(
        "Enable FIRS e-Invoice",
        default=False,
        help="Enable automatic e-Invoice submission to FIRS TaxPro Max portal",
    )
    firs_api_url = fields.Char(
        "FIRS API URL",
        default="https://api.taxpromax.com/einvoice/v1",
        help="Base URL for FIRS e-Invoice API (e.g., https://eivc-k6z6d.ondigitalocean.app/api). Used for connection test (GET request).",
    )
    firs_api_endpoint = fields.Char(
        "FIRS API Endpoint Path",
        default="/api/v1/invoice/sign",
        help="Endpoint path for invoice submission (POST request). Default: /api/v1/invoice/sign. If base URL ends with /api, use /v1/invoice/sign instead.",
    )
    firs_environment = fields.Selection(
        [("sandbox", "Sandbox (Test)"), ("prod", "Production (Live)")],
        string="Environment",
        default="sandbox",
        help="Use Sandbox for testing, Production for live invoices",
    )
    firs_tin = fields.Char(
        "Company TIN",
        help="Your company's Tax Identification Number registered with FIRS",
    )

    # Modern API credentials
    firs_entry_id = fields.Char("Entry ID", help="Entry ID from FIRS TaxPro Max portal")
    firs_service_id = fields.Char(
        "Service ID", 
        help="Service ID (8 characters, alphanumeric) assigned by FIRS upon business enablement. Required for IRN generation. Format: e.g., 94ND90NR"
    )
    firs_business_id = fields.Char(
        "Business ID", help="Business ID from FIRS TaxPro Max portal"
    )
    firs_api_key = fields.Char(
        "API Key", help="API Key generated from FIRS TaxPro Max portal"
    )
    firs_client_secret = fields.Char(
        "API Secret", help="API Secret (Secret Key) generated from FIRS TaxPro Max portal. Used as x-api-secret header."
    )
    firs_irn_template = fields.Char(
        "IRN Template", help="Invoice Reference Number template format"
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()

        res.update(
            {
                "firs_enabled": ICP.get_param("firs.enabled", default=False),
                "firs_api_url": ICP.get_param(
                    "firs.api_url", default="https://api.taxpromax.com/einvoice/v1"
                ),
                "firs_api_endpoint": ICP.get_param(
                    "firs.api_endpoint", default="/api/v1/invoice/sign"
                ),
                "firs_environment": ICP.get_param(
                    "firs.environment", default="sandbox"
                ),
                "firs_tin": ICP.get_param("firs.tin", default=""),
                "firs_entry_id": ICP.get_param("firs.entry_id", default=""),
                "firs_service_id": ICP.get_param("firs.service_id", default=""),
                "firs_business_id": ICP.get_param("firs.business_id", default=""),
                "firs_api_key": ICP.get_param("firs.api_key", default=""),
                "firs_client_secret": ICP.get_param("firs.client_secret", default=""),
                "firs_irn_template": ICP.get_param("firs.irn_template", default=""),
            }
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()

        ICP.set_param("firs.enabled", self.firs_enabled)
        ICP.set_param("firs.api_url", self.firs_api_url or "")
        ICP.set_param("firs.api_endpoint", self.firs_api_endpoint or "/api/v1/invoice/sign")
        ICP.set_param("firs.environment", self.firs_environment or "sandbox")
        ICP.set_param("firs.tin", self.firs_tin or "")
        ICP.set_param("firs.entry_id", self.firs_entry_id or "")
        ICP.set_param("firs.service_id", self.firs_service_id or "")
        ICP.set_param("firs.business_id", self.firs_business_id or "")
        ICP.set_param("firs.api_key", self.firs_api_key or "")
        ICP.set_param("firs.client_secret", self.firs_client_secret or "")
        ICP.set_param("firs.irn_template", self.firs_irn_template or "")

    def action_test_connection(self):
        """Test FIRS connection using configured credentials"""
        if not self.firs_enabled:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "FIRS Connection",
                    "message": "Please enable FIRS e-Invoice integration first.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        if not self.firs_api_url:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "FIRS Connection",
                    "message": "FIRS API URL not configured.",
                    "type": "warning",
                    "sticky": False,
                },
            }

        headers = {"Content-Type": "application/json"}
        if self.firs_api_key:
            headers["x-api-key"] = self.firs_api_key
        if self.firs_client_secret:
            headers["x-api-secret"] = self.firs_client_secret
        if self.firs_entry_id:
            headers["x-entry-id"] = self.firs_entry_id
        if self.firs_business_id:
            headers["x-business-id"] = self.firs_business_id

        try:
            # Connection test uses GET request to the base /api endpoint
            # This is different from invoice submission which uses POST to /api/einvoice/post
            resp = requests.get(self.firs_api_url, headers=headers, timeout=10)
            status = resp.status_code

            if 200 <= status < 300:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "FIRS Connection",
                        "message": f"✅ Connection successful (HTTP {status}).",
                        "type": "success",
                        "sticky": False,
                    },
                }
            else:
                _logger.warning(
                    "FIRS connection test returned non-2xx: %s %s", status, resp.text[:1000]
                )
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "FIRS Connection",
                        "message": f"❌ Connection failed (HTTP {status}). See logs.",
                        "type": "danger",
                        "sticky": True,
                    },
                }

        except Exception as e:
            _logger.exception("FIRS connection test error: %s", e)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "FIRS Connection",
                    "message": f"❌ Connection error: {str(e)}",
                    "type": "danger",
                    "sticky": True,
                },
            }
