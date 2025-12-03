from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ScanTrackingWizard(models.TransientModel):
    _name = "scan.tracking.wizard"
    _description = "Scan Tracking ID Wizard"

    tracking_id = fields.Char("Tracking ID", required=True)

    def action_scan(self):
        tracking_id = (self.tracking_id or "").strip()
        if not tracking_id:
            raise UserError(_("Please enter or scan a Tracking ID."))
        order = self.env["package.order"].fetch_from_dellyman(tracking_id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "package.order",
            "res_id": order.id,
            "view_mode": "form",
            "target": "current",
        }
