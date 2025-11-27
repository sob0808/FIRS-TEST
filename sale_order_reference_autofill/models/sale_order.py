from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        # Set reference to SO number if empty
        if not order.reference:
            order.reference = order.name
        return order
