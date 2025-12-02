
from odoo import models, fields, api

class PackageOrder(models.Model):
    _name = "package.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Package Order"

    name = fields.Char(required=True, tracking=True)
    ord_id = fields.Char()
    batch_id = fields.Many2one("package.batch")
    package_description = fields.Text()
    customer_name = fields.Char()
    customer_phone = fields.Char()
    customer_address = fields.Char()
    current_status = fields.Selection([
        ("received", "Received"),
        ("assigned", "Assigned"),
        ("picked", "Picked"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("awaiting_return", "Awaiting Return"),
        ("returned", "Returned")
    ], default="received", tracking=True)

    location_id = fields.Many2one("package.location", string="Location")

    def action_set_status(self, status):
        for rec in self:
            rec.current_status = status
